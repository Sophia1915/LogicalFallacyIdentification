from flask import Flask, render_template, request, session, redirect, url_for

from LinkChatGPTNEW import generate_responses, fallacies, get_explanation
from fuzzywuzzy import process
import random
import Levenshtein
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'Debate>MUN'

def normalize_answer(answer):
  if answer.lower().endswith("fallacy"):
      answer = answer[:-7]  # remove the last 7 characters ("fallacy")
  return answer.strip().lower()


@app.route('/index', methods=['GET'])
def index():
  return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        return game()
    return redirect(url_for('index'))

@app.route('/learn')
def learn():
    return render_template('learn.html')

@app.route('/instruction', methods=['GET'])
def instruction():
    return render_template('instruction.html')

@app.route('/game', methods=['GET', 'POST'])
def game():
    
  message = ""
  correct_message = "Correct! Well done!"
  explanation = None
  options = None

  if request.method == 'POST':
    user_answer = request.form.get('answer')
    user_answer = normalize_answer(user_answer)

    if 'was_multiple_choice' in session and session['was_multiple_choice']:
      current_fallacy = session.get('current_fallacy')
      if not current_fallacy:
        message = "Something went wrong. Please try again."
      elif user_answer and user_answer.lower() == current_fallacy.lower():
        message = correct_message
        assistant_responses, current_fallacy = generate_responses()
        session['current_fallacy'] = current_fallacy
        session['assistant_responses'] = assistant_responses
        session['was_multiple_choice'] = False
      else:
        message = f"Oops! The correct answer was {current_fallacy}."
        example = session.get('assistant_responses')[0]
        explanation = get_explanation(current_fallacy, example)
        session['was_multiple_choice'] = False
        return render_template('game.html',
                               responses=session.get('assistant_responses'),
                               message=message,
                               explanation=explanation,
                               fallacies=fallacies)
    else:
      best_match, score = process.extractOne(user_answer, fallacies)
      if score > 80 and session.get('current_fallacy').lower() == best_match:
        message = correct_message
        assistant_responses, current_fallacy = generate_responses()
        session['current_fallacy'] = current_fallacy
        session['assistant_responses'] = assistant_responses
      else:
        message = f"Not quite! Let's try again:"
        options = generate_multiple_choice(session.get('current_fallacy'))
        session['was_multiple_choice'] = True
        return render_template('game.html',
                               responses=session.get('assistant_responses'),
                               message=message,
                               options=options,
                               fallacies=fallacies)

  else:
    assistant_responses, current_fallacy = generate_responses()
    session['current_fallacy'] = current_fallacy
    session['assistant_responses'] = assistant_responses

  return render_template('game.html',
                         responses=assistant_responses,
                         message=message,
                         options=options,
                         fallacies=fallacies)


@app.route('/continue', methods=['POST'])
def continue_game():
  # Get new example and reset values
  assistant_responses, current_fallacy = generate_responses()
  session['current_fallacy'] = current_fallacy
  session['assistant_responses'] = assistant_responses
  session['was_multiple_choice'] = False
  return render_template('game.html',
                         responses=assistant_responses,
                         message="",
                         fallacies=fallacies)


def generate_multiple_choice(correct_answer):
  options = [correct_answer]
  while len(options) < 4:
    choice = random.choice(fallacies)
    if choice not in options:
      options.append(choice)
  random.shuffle(options)
  return options


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8081)  