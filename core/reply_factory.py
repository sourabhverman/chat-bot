from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if current_question_id is None:  # quiz starting
        bot_responses.append(BOT_WELCOME_MESSAGE)
        current_question_id = -1  # no question answered yet

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    # Do not validate if it's the very beginning (no question asked yet)
    if current_question_id == -1:
        return True, ""

    if current_question_id >= len(PYTHON_QUESTION_LIST):
        return False, "Invalid question ID."

    correct_answer = PYTHON_QUESTION_LIST[current_question_id]["answer"]

    # Initialize answers dict in session
    if "user_answers" not in session:
        session["user_answers"] = {}

    # Store whether the user got it right or not
    session["user_answers"][current_question_id] = {
        "given_answer": answer.strip(),
        "is_correct": answer.strip().lower() == correct_answer.lower()
    }

    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    next_id = current_question_id + 1

    if next_id < len(PYTHON_QUESTION_LIST):
        return PYTHON_QUESTION_LIST[next_id]["question"], next_id
    else:
        return None, -1


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    user_answers = session.get("user_answers", {})

    score = sum(1 for ans in user_answers.values() if ans["is_correct"])
    total = len(PYTHON_QUESTION_LIST)

    result_message = f"🎉 Quiz Completed! You scored {score} out of {total}.\n\n"

    # Show detailed feedback
    for idx, q in enumerate(PYTHON_QUESTION_LIST):
        given = user_answers.get(idx, {}).get("given_answer", "No answer")
        correctness = "✅ Correct" if user_answers.get(idx, {}).get("is_correct", False) else f"❌ Wrong (Correct: {q['answer']})"
        result_message += f"Q{idx+1}: {q['question']}\nYour answer: {given}\n{correctness}\n\n"

    return result_message.strip()
