import streamlit as st
import random
import json
from datetime import datetime
import pandas as pd

# Try to import vocab data
try:
    from data.vocab_data import vocab_groups
except ImportError:
    # Fallback minimal vocabulary for testing
    vocab_groups = {
        "Group 1": [
            {"word": "abound", "simple": "be plentiful", "meaning": "প্রচুর থাকা"},
            {"word": "austere", "simple": "strict, plain, simple", "meaning": "কঠোর, সাধারণ, সরল"},
            {"word": "capricious", "simple": "impulsive, unpredictable", "meaning": "আবেগপ্রবণ, অনিয়মিত"},
        ]
    }

# Page configuration
st.set_page_config(
    page_title="GRE Vocabulary Master",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-bottom: 1rem;
    }
    .flashcard {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        min-height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    .flashcard:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    }
    .word-display {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .simple-def {
        font-size: 1.5rem;
        font-style: italic;
        margin-bottom: 1.5rem;
        opacity: 0.9;
    }
    .meaning-display {
        font-size: 1.8rem;
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1rem;
        width: 100%;
    }
    .score-badge {
        background: #10B981;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .progress-bar {
        height: 10px;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .test-question {
        background: #F3F4F6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'current_group' not in st.session_state:
        st.session_state.current_group = list(vocab_groups.keys())[0]
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'total_questions' not in st.session_state:
        st.session_state.total_questions = 0
    if 'test_results' not in st.session_state:
        st.session_state.test_results = []
    if 'progress' not in st.session_state:
        st.session_state.progress = {}
        for group in vocab_groups.keys():
            st.session_state.progress[group] = {
                "studied": False,
                "test_taken": False,
                "best_score": 0,
                "last_attempt": None,
                "cards_viewed": 0
            }
    if 'flashcard_index' not in st.session_state:
        st.session_state.flashcard_index = 0
    if 'show_meaning' not in st.session_state:
        st.session_state.show_meaning = False
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

init_session_state()

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>📚 GRE Vocabulary Master</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Navigation
    app_mode = st.selectbox(
        "Navigate to:",
        ["🏠 Dashboard", "📖 Study Mode", "🧪 Test Yourself", "🎮 Games", "📊 Progress Report", "⚙️ Settings"]
    )
    
    st.markdown("---")
    
    # Group selection
    st.subheader("Select Vocabulary Group")
    groups = list(vocab_groups.keys())
    selected_group = st.selectbox(
        "Choose a group:",
        groups,
        index=groups.index(st.session_state.current_group) if st.session_state.current_group in groups else 0,
        key="group_selector"
    )
    
    if selected_group != st.session_state.current_group:
        st.session_state.current_group = selected_group
        st.session_state.flashcard_index = 0
        st.session_state.show_meaning = False
        st.rerun()
    
    # Group info
    current_words = vocab_groups[selected_group]
    studied = st.session_state.progress[selected_group]["studied"]
    status = "✅ Studied" if studied else "📖 In Progress"
    
    st.markdown(f"**Status:** {status}")
    st.markdown(f"**Words:** {len(current_words)}")
    st.markdown(f"**Cards Viewed:** {st.session_state.progress[selected_group]['cards_viewed']}")
    
    if st.session_state.progress[selected_group]["test_taken"]:
        st.markdown(f"**Best Score:** {st.session_state.progress[selected_group]['best_score']}%")
    
    st.markdown("---")
    
    # Quick stats
    st.subheader("Quick Stats")
    studied_count = sum(1 for group, data in st.session_state.progress.items() if data["studied"])
    total_groups = len(vocab_groups)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Groups Studied", f"{studied_count}/{total_groups}")
    with col2:
        if st.session_state.total_questions > 0:
            accuracy = (st.session_state.score / st.session_state.total_questions) * 100
            st.metric("Accuracy", f"{accuracy:.1f}%")
        else:
            st.metric("Accuracy", "0%")
    
    st.markdown("---")
    
    # Reset button
    if st.button("🔄 Reset All Progress", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key != 'dark_mode':
                del st.session_state[key]
        init_session_state()
        st.success("Progress reset successfully!")
        st.rerun()

# Main content based on navigation
if app_mode == "🏠 Dashboard":
    st.markdown("<h1 class='main-header'>Welcome to GRE Vocabulary Master! 🎓</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Master 1000+ GRE words with interactive learning</p>", unsafe_allow_html=True)
    
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_words = sum(len(words) for words in vocab_groups.values())
        st.metric("Total Words", total_words)
    
    with col2:
        st.metric("Groups", len(vocab_groups))
    
    with col3:
        tests_taken = sum(1 for data in st.session_state.progress.values() if data["test_taken"])
        st.metric("Tests Taken", tests_taken)
    
    with col4:
        if st.session_state.total_questions > 0:
            st.metric("Total Practice", st.session_state.total_questions)
        else:
            st.metric("Total Practice", "0")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Start Studying", use_container_width=True, help="Jump into study mode"):
            st.session_state.app_mode = "📖 Study Mode"
            st.rerun()
    
    with col2:
        if st.button("🧪 Take a Test", use_container_width=True, help="Test your knowledge"):
            st.session_state.app_mode = "🧪 Test Yourself"
            st.rerun()
    
    with col3:
        if st.button("🎮 Play a Game", use_container_width=True, help="Learn through games"):
            st.session_state.app_mode = "🎮 Games"
            st.rerun()
    
    # Recent activity
    st.subheader("Recent Activity")
    if st.session_state.test_results:
        latest_results = st.session_state.test_results[-3:]  # Last 3 tests
        for result in reversed(latest_results):
            with st.expander(f"{result['date']} - {result['group']} - Score: {result['score']}"):
                st.write(f"**Type:** {result.get('type', 'Multiple Choice')}")
                st.write(f"**Score:** {result['score']}")
                st.write(f"**Time:** {result.get('time_taken', 'N/A')}")
    else:
        st.info("No test results yet. Take your first test to see activity here!")
    
    # Progress chart
    st.subheader("Learning Progress")
    progress_data = []
    for group, data in st.session_state.progress.items():
        progress_data.append({
            "Group": group,
            "Studied": "Yes" if data["studied"] else "No",
            "Best Score": data["best_score"],
            "Cards Viewed": data["cards_viewed"]
        })
    
    if progress_data:
        df = pd.DataFrame(progress_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

elif app_mode == "📖 Study Mode":
    st.markdown("<h1 class='main-header'>📖 Study Mode</h1>", unsafe_allow_html=True)
    
    current_group = vocab_groups[st.session_state.current_group]
    
    # Study mode tabs
    tab1, tab2, tab3 = st.tabs(["🎴 Flashcards", "📋 Word List", "🔊 Pronunciation"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if current_group:
                idx = st.session_state.flashcard_index % len(current_group)
                word_data = current_group[idx]
                
                # Update cards viewed
                if st.session_state.flashcard_index > st.session_state.progress[st.session_state.current_group]["cards_viewed"]:
                    st.session_state.progress[st.session_state.current_group]["cards_viewed"] = st.session_state.flashcard_index
                
                # Flashcard
                st.markdown(f"""
                <div class="flashcard">
                    <div class="word-display">{word_data['word']}</div>
                    <div class="simple-def">{word_data['simple']}</div>
                    {f'<div class="meaning-display">{word_data["meaning"]}</div>' if st.session_state.show_meaning else ''}
                </div>
                """, unsafe_allow_html=True)
                
                # Card controls
                col_btns = st.columns(5)
                
                with col_btns[0]:
                    if st.button("⏮️", help="First card", use_container_width=True):
                        st.session_state.flashcard_index = 0
                        st.session_state.show_meaning = False
                        st.rerun()
                
                with col_btns[1]:
                    if st.button("◀️", help="Previous card", use_container_width=True):
                        st.session_state.flashcard_index = max(0, st.session_state.flashcard_index - 1)
                        st.session_state.show_meaning = False
                        st.rerun()
                
                with col_btns[2]:
                    btn_text = "👁️ Show" if not st.session_state.show_meaning else "🙈 Hide"
                    if st.button(btn_text, help="Show/Hide meaning", use_container_width=True):
                        st.session_state.show_meaning = not st.session_state.show_meaning
                        st.rerun()
                
                with col_btns[3]:
                    if st.button("▶️", help="Next card", use_container_width=True):
                        st.session_state.flashcard_index += 1
                        st.session_state.show_meaning = False
                        st.rerun()
                
                with col_btns[4]:
                    if st.button("⏭️", help="Last card", use_container_width=True):
                        st.session_state.flashcard_index = len(current_group) - 1
                        st.session_state.show_meaning = False
                        st.rerun()
                
                # Progress
                progress = ((idx) + 1) / len(current_group)
                st.progress(progress)
                st.caption(f"Card {idx + 1} of {len(current_group)}")
                
                # Mark as studied
                if not st.session_state.progress[st.session_state.current_group]["studied"]:
                    if st.button("✅ Mark This Group as Studied", use_container_width=True):
                        st.session_state.progress[st.session_state.current_group]["studied"] = True
                        st.success(f"Great! You've completed studying {st.session_state.current_group}")
                        st.rerun()
    
    with tab2:
        st.subheader(f"Word List - {st.session_state.current_group}")
        
        # Search filter
        search_term = st.text_input("🔍 Search words in this group:", "")
        
        # Display words
        words_to_display = current_group
        if search_term:
            words_to_display = [
                w for w in current_group 
                if search_term.lower() in w['word'].lower() 
                or search_term.lower() in w['simple'].lower()
                or search_term.lower() in w['meaning'].lower()
            ]
        
        for i, word_data in enumerate(words_to_display, 1):
            with st.expander(f"{i}. {word_data['word']}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Simple Definition:**")
                    st.info(word_data['simple'])
                with col2:
                    st.write(f"**Meaning:**")
                    st.success(word_data['meaning'])
                
                # Quick actions for each word
                col_act = st.columns(3)
                with col_act[0]:
                    if st.button("📌 Save", key=f"save_{word_data['word']}", help="Save word for review"):
                        st.toast(f"Saved '{word_data['word']}' for later review!")
                with col_act[1]:
                    if st.button("🎧 Hear", key=f"hear_{word_data['word']}", help="Listen to pronunciation"):
                        st.toast(f"Pronunciation for '{word_data['word']}' (audio would play here)")
                with col_act[2]:
                    if st.button("📝 Example", key=f"ex_{word_data['word']}", help="See example sentence"):
                        st.info(f"Example: He used '{word_data['word']}' in his speech effectively.")
        
        st.metric("Words Found", len(words_to_display))
    
    with tab3:
        st.subheader("Pronunciation Guide")
        st.info("🔊 Select a word to hear its pronunciation")
        
        word_list = [w['word'] for w in current_group]
        selected_word = st.selectbox("Choose a word:", word_list)
        
        if selected_word:
            word_data = next(w for w in current_group if w['word'] == selected_word)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### {selected_word}")
                st.write(f"**Definition:** {word_data['simple']}")
                st.write(f"**Meaning:** {word_data['meaning']}")
            
            with col2:
                st.markdown("### 🔊 Pronunciation")
                st.write("(Audio player would appear here)")
                st.write("**Phonetic Spelling:** /əˈbaʊnd/")
                st.write("**Syllables:** a-bound")
                
                if st.button("▶️ Play Pronunciation", use_container_width=True):
                    st.toast(f"Playing pronunciation for '{selected_word}'")

elif app_mode == "🧪 Test Yourself":
    st.markdown("<h1 class='main-header'>🧪 Test Yourself</h1>", unsafe_allow_html=True)
    
    current_group = vocab_groups[st.session_state.current_group]
    
    # Test configuration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        test_type = st.selectbox(
            "Test Type:",
            ["Multiple Choice", "Fill in the Blank", "True/False", "Mixed Questions"]
        )
    
    with col2:
        num_questions = st.slider(
            "Number of Questions:",
            min_value=5,
            max_value=min(30, len(current_group)),
            value=min(10, len(current_group)),
            step=5
        )
    
    with col3:
        difficulty = st.selectbox(
            "Difficulty:",
            ["Easy", "Medium", "Hard", "Expert"]
        )
    
    # Initialize test session
    if 'test_in_progress' not in st.session_state:
        st.session_state.test_in_progress = False
    
    if 'test_data' not in st.session_state:
        st.session_state.test_data = None
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    
    # Start test button
    if not st.session_state.test_in_progress:
        if st.button("🚀 Start Test", type="primary", use_container_width=True):
            # Prepare test questions
            test_words = random.sample(current_group, min(num_questions, len(current_group)))
            
            test_data = []
            for word_data in test_words:
                question_type = test_type
                if test_type == "Mixed Questions":
                    question_type = random.choice(["Multiple Choice", "Fill in the Blank", "True/False"])
                
                if question_type == "Multiple Choice":
                    # Generate multiple choice question
                    all_words = [w['meaning'] for w in current_group if w['meaning'] != word_data['meaning']]
                    wrong_answers = random.sample(all_words, min(3, len(all_words)))
                    options = wrong_answers + [word_data['meaning']]
                    random.shuffle(options)
                    
                    test_data.append({
                        "type": "multiple_choice",
                        "word": word_data['word'],
                        "correct_answer": word_data['meaning'],
                        "options": options,
                        "question": f"What does '{word_data['word']}' mean?",
                        "simple_def": word_data['simple']
                    })
                
                elif question_type == "Fill in the Blank":
                    test_data.append({
                        "type": "fill_blank",
                        "word": word_data['word'],
                        "correct_answer": word_data['simple'],
                        "question": f"'{word_data['word']}' means: _________",
                        "hint": word_data['meaning']
                    })
                
                elif question_type == "True/False":
                    # Sometimes make it false
                    is_true = random.choice([True, False])
                    if is_true:
                        statement = f"'{word_data['word']}' means: {word_data['simple']}"
                        correct_answer = "True"
                    else:
                        # Pick a wrong definition
                        other_words = [w for w in current_group if w['word'] != word_data['word']]
                        wrong_word = random.choice(other_words)
                        statement = f"'{word_data['word']}' means: {wrong_word['simple']}"
                        correct_answer = "False"
                    
                    test_data.append({
                        "type": "true_false",
                        "word": word_data['word'],
                        "correct_answer": correct_answer,
                        "statement": statement,
                        "actual_meaning": word_data['meaning']
                    })
            
            st.session_state.test_data = test_data
            st.session_state.test_in_progress = True
            st.session_state.current_question = 0
            st.session_state.user_answers = []
            st.session_state.test_start_time = datetime.now()
            st.rerun()
    
    # Display test questions
    if st.session_state.test_in_progress and st.session_state.test_data:
        test_data = st.session_state.test_data
        current_q = st.session_state.current_question
        
        if current_q < len(test_data):
            question = test_data[current_q]
            
            st.markdown(f"### Question {current_q + 1} of {len(test_data)}")
            
            # Progress bar
            progress = (current_q + 1) / len(test_data)
            st.progress(progress)
            
            # Display question based on type
            if question["type"] == "multiple_choice":
                st.markdown(f"#### {question['question']}")
                st.caption(f"Hint: {question['simple_def']}")
                
                selected = st.radio(
                    "Select your answer:",
                    question["options"],
                    key=f"q_{current_q}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Submit Answer", use_container_width=True, type="primary"):
                        st.session_state.user_answers.append({
                            "question": question["question"],
                            "user_answer": selected,
                            "correct_answer": question["correct_answer"],
                            "is_correct": selected == question["correct_answer"]
                        })
                        st.session_state.current_question += 1
                        st.rerun()
                
                with col2:
                    if st.button("⏭️ Skip Question", use_container_width=True):
                        st.session_state.user_answers.append({
                            "question": question["question"],
                            "user_answer": "Skipped",
                            "correct_answer": question["correct_answer"],
                            "is_correct": False
                        })
                        st.session_state.current_question += 1
                        st.rerun()
            
            elif question["type"] == "fill_blank":
                st.markdown(f"#### {question['question']}")
                st.caption(f"Hint: {question['hint']}")
                
                user_answer = st.text_input("Your answer:", key=f"q_{current_q}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Submit Answer", use_container_width=True, type="primary"):
                        # Simple check - could be improved
                        is_correct = question["correct_answer"].lower() in user_answer.lower()
                        st.session_state.user_answers.append({
                            "question": question["question"],
                            "user_answer": user_answer,
                            "correct_answer": question["correct_answer"],
                            "is_correct": is_correct
                        })
                        st.session_state.current_question += 1
                        st.rerun()
                
                with col2:
                    if st.button("⏭️ Skip Question", use_container_width=True):
                        st.session_state.user_answers.append({
                            "question": question["question"],
                            "user_answer": "Skipped",
                            "correct_answer": question["correct_answer"],
                            "is_correct": False
                        })
                        st.session_state.current_question += 1
                        st.rerun()
            
            elif question["type"] == "true_false":
                st.markdown(f"#### {question['statement']}")
                
                selected = st.radio(
                    "Is this statement true or false?",
                    ["True", "False"],
                    key=f"q_{current_q}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Submit Answer", use_container_width=True, type="primary"):
                        st.session_state.user_answers.append({
                            "question": question["statement"],
                            "user_answer": selected,
                            "correct_answer": question["correct_answer"],
                            "is_correct": selected == question["correct_answer"]
                        })
                        st.session_state.current_question += 1
                        st.rerun()
                
                with col2:
                    if st.button("⏭️ Skip Question", use_container_width=True):
                        st.session_state.user_answers.append({
                            "question": question["statement"],
                            "user_answer": "Skipped",
                            "correct_answer": question["correct_answer"],
                            "is_correct": False
                        })
                        st.session_state.current_question += 1
                        st.rerun()
        
        else:
            # Test completed
            test_end_time = datetime.now()
            time_taken = (test_end_time - st.session_state.test_start_time).seconds
            
            # Calculate score
            correct = sum(1 for ans in st.session_state.user_answers if ans["is_correct"])
            total = len(st.session_state.user_answers)
            score_percent = (correct / total) * 100 if total > 0 else 0
            
            # Update session state
            st.session_state.score += correct
            st.session_state.total_questions += total
            
            # Update progress for this group
            st.session_state.progress[st.session_state.current_group]["test_taken"] = True
            st.session_state.progress[st.session_state.current_group]["best_score"] = max(
                st.session_state.progress[st.session_state.current_group]["best_score"],
                score_percent
            )
            st.session_state.progress[st.session_state.current_group]["last_attempt"] = datetime.now().strftime("%Y-%m-%d")
            
            # Save test result
            test_result = {
                'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'group': st.session_state.current_group,
                'score': f"{correct}/{total}",
                'percentage': score_percent,
                'type': test_type,
                'time_taken': f"{time_taken} seconds",
                'details': st.session_state.user_answers
            }
            st.session_state.test_results.append(test_result)
            
            # Display results
            st.balloons()
            st.markdown("<h2 style='text-align: center; color: #10B981;'>🎉 Test Completed! 🎉</h2>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Your Score", f"{correct}/{total}")
            with col2:
                st.metric("Percentage", f"{score_percent:.1f}%")
            with col3:
                st.metric("Time Taken", f"{time_taken} sec")
            
            # Performance feedback
            if score_percent >= 90:
                st.success("🌟 Outstanding! You've mastered this group!")
            elif score_percent >= 75:
                st.success("👍 Excellent work! Keep it up!")
            elif score_percent >= 60:
                st.warning("📚 Good effort! Review the missed words.")
            else:
                st.info("📖 Needs improvement. Study this group again.")
            
            # Detailed results
            with st.expander("📋 View Detailed Results", expanded=True):
                for i, ans in enumerate(st.session_state.user_answers, 1):
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if ans["is_correct"]:
                            st.success(f"Q{i}")
                        else:
                            st.error(f"Q{i}")
                    with col2:
                        st.write(f"**Question:** {ans['question']}")
                        st.write(f"**Your answer:** {ans['user_answer']}")
                        st.write(f"**Correct answer:** {ans['correct_answer']}")
                        st.write("---")
            
            # Actions after test
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📊 Review Group", use_container_width=True):
                    st.session_state.app_mode = "📖 Study Mode"
                    st.rerun()
            with col2:
                if st.button("🧪 Take Another Test", use_container_width=True, type="primary"):
                    st.session_state.test_in_progress = False
                    st.session_state.test_data = None
                    st.session_state.current_question = 0
                    st.session_state.user_answers = []
                    st.rerun()
            with col3:
                if st.button("🏠 Back to Dashboard", use_container_width=True):
                    st.session_state.test_in_progress = False
                    st.session_state.test_data = None
                    st.rerun()
    
    elif not st.session_state.test_in_progress:
        st.info("Configure your test settings above and click 'Start Test' to begin.")

elif app_mode == "🎮 Games":
    st.markdown("<h1 class='main-header'>🎮 Learning Games</h1>", unsafe_allow_html=True)
    
    current_group = vocab_groups[st.session_state.current_group]
    
    game_choice = st.selectbox(
        "Choose a game:",
        ["Word Match", "Memory Game", "Word Scramble", "Speed Challenge"]
    )
    
    if game_choice == "Word Match":
        st.subheader("🔤 Word Match Game")
        st.write("Match words with their correct definitions!")
        
        if st.button("🎯 Start Matching Game", use_container_width=True):
            game_words = random.sample(current_group, min(8, len(current_group)))
            
            # Prepare game state
            st.session_state.game_words = [w['word'] for w in game_words]
            st.session_state.game_defs = [w['simple'] for w in game_words]
            random.shuffle(st.session_state.game_defs)
            
            st.session_state.game_correct = {w['word']: w['simple'] for w in game_words}
            st.session_state.game_matches = {}
            st.session_state.game_started = True
        
        if 'game_started' in st.session_state and st.session_state.game_started:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Words")
                for word in st.session_state.game_words:
                    st.write(f"• **{word}**")
            
            with col2:
                st.write("### Definitions")
                for i, definition in enumerate(st.session_state.game_defs):
                    st.write(f"{i+1}. {definition}")
            
            # Matching interface
            st.write("### Make Your Matches")
            for word in st.session_state.game_words:
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.write(f"**{word}**")
                with col2:
                    selected_def = st.selectbox(
                        f"Match for {word}:",
                        [""] + st.session_state.game_defs,
                        key=f"match_{word}"
                    )
                    if selected_def:
                        st.session_state.game_matches[word] = selected_def
            
            if st.button("✅ Check Matches", use_container_width=True):
                correct = 0
                total = len(st.session_state.game_words)
                
                for word in st.session_state.game_words:
                    if word in st.session_state.game_matches:
                        if st.session_state.game_matches[word] == st.session_state.game_correct[word]:
                            correct += 1
                
                st.success(f"Score: {correct}/{total}")
                
                if correct == total:
                    st.balloons()
                    st.balloons()
                    st.success("🎉 Perfect! All matches correct!")
                
                # Show answers
                with st.expander("Show Answers"):
                    for word, correct_def in st.session_state.game_correct.items():
                        user_match = st.session_state.game_matches.get(word, "No match")
                        if user_match == correct_def:
                            st.write(f"✅ **{word}** → {correct_def}")
                        else:
                            st.write(f"❌ **{word}** → Your: '{user_match}' | Correct: '{correct_def}'")

elif app_mode == "📊 Progress Report":
    st.markdown("<h1 class='main-header'>📊 Your Learning Progress</h1>", unsafe_allow_html=True)
    
    # Overall statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        studied_groups = sum(1 for data in st.session_state.progress.values() if data["studied"])
        st.metric("Groups Completed", f"{studied_groups}/{len(vocab_groups)}")
    
    with col2:
        tests_taken = sum(1 for data in st.session_state.progress.values() if data["test_taken"])
        st.metric("Tests Taken", tests_taken)
    
    with col3:
        total_cards = sum(data["cards_viewed"] for data in st.session_state.progress.values())
        st.metric("Cards Viewed", total_cards)
    
    with col4:
        if st.session_state.total_questions > 0:
            overall_accuracy = (st.session_state.score / st.session_state.total_questions) * 100
            st.metric("Overall Accuracy", f"{overall_accuracy:.1f}%")
        else:
            st.metric("Overall Accuracy", "0%")
    
    st.markdown("---")
    
    # Group-wise progress
    st.subheader("📈 Group-wise Progress")
    
    progress_data = []
    for group, data in st.session_state.progress.items():
        progress_data.append({
            "Group": group,
            "Status": "✅ Completed" if data["studied"] else "📖 In Progress",
            "Best Score": f"{data['best_score']}%" if data['best_score'] > 0 else "Not Taken",
            "Cards Viewed": data["cards_viewed"],
            "Last Attempt": data["last_attempt"] or "Never"
        })
    
    if progress_data:
        df = pd.DataFrame(progress_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Visual progress
        st.subheader("📊 Progress Visualization")
        
        # Completion chart
        completion_data = {
            "Completed": studied_groups,
            "Remaining": len(vocab_groups) - studied_groups
        }
        
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(completion_data)
        
        with col2:
            # Test scores
            scores = [data["best_score"] for data in st.session_state.progress.values() if data["test_taken"]]
            if scores:
                avg_score = sum(scores) / len(scores)
                st.metric("Average Test Score", f"{avg_score:.1f}%")
    
    # Test history
    st.subheader("📋 Test History")
    if st.session_state.test_results:
        for result in reversed(st.session_state.test_results[-10:]):  # Last 10 tests
            with st.expander(f"{result['date']} - {result['group']} - Score: {result['score']} ({result['percentage']:.1f}%)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Test Type:** {result.get('type', 'N/A')}")
                    st.write(f"**Time Taken:** {result.get('time_taken', 'N/A')}")
                with col2:
                    st.write(f"**Score:** {result['score']}")
                    st.write(f"**Percentage:** {result['percentage']:.1f}%")
                
                # Performance indicator
                if result['percentage'] >= 80:
                    st.success("Excellent Performance")
                elif result['percentage'] >= 60:
                    st.warning("Good Performance")
                else:
                    st.info("Needs Improvement")
    else:
        st.info("No test history available yet. Take some tests to see your progress here!")

elif app_mode == "⚙️ Settings":
    st.markdown("<h1 class='main-header'>⚙️ Settings</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Appearance")
        
        # Dark mode toggle
        dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.info("Dark mode setting changed. Refresh to see effect.")
        
        # Font size
        font_size = st.select_slider(
            "Font Size",
            options=["Small", "Medium", "Large"],
            value="Medium"
        )
        
        # Card style
        card_style = st.selectbox(
            "Flashcard Style",
            ["Default", "Minimal", "Colorful", "Professional"]
        )
    
    with col2:
        st.subheader("Study Preferences")
        
        # Default test length
        default_test_length = st.slider(
            "Default Test Length",
            min_value=5,
            max_value=30,
            value=10,
            step=5
        )
        
        # Auto-advance cards
        auto_advance = st.toggle("Auto-advance flashcards", value=False)
        if auto_advance:
            advance_speed = st.slider("Advance every (seconds)", 2, 10, 5)
        
        # Show hints
        show_hints = st.toggle("Show hints in tests", value=True)
    
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export data
        if st.button("📤 Export Progress Data", use_container_width=True):
            # Create export data
            export_data = {
                "progress": st.session_state.progress,
                "test_results": st.session_state.test_results,
                "score": st.session_state.score,
                "total_questions": st.session_state.total_questions,
                "export_date": datetime.now().isoformat()
            }
            
            # Convert to JSON
            json_data = json.dumps(export_data, indent=2)
            
            # Create download button
            st.download_button(
                label="Download Progress Data",
                data=json_data,
                file_name="gre_vocab_progress.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col2:
        # Import data
        uploaded_file = st.file_uploader("Import progress data", type=['json'])
        if uploaded_file is not None:
            try:
                import_data = json.load(uploaded_file)
                st.success("Data loaded successfully! Click below to import.")
                
                if st.button("📥 Import Progress Data", use_container_width=True, type="primary"):
                    # Update session state with imported data
                    if "progress" in import_data:
                        st.session_state.progress.update(import_data["progress"])
                    if "test_results" in import_data:
                        st.session_state.test_results = import_data["test_results"]
                    if "score" in import_data:
                        st.session_state.score = import_data["score"]
                    if "total_questions" in import_data:
                        st.session_state.total_questions = import_data["total_questions"]
                    
                    st.success("Progress data imported successfully!")
                    st.rerun()
            except:
                st.error("Error importing data. Please check the file format.")
    
    st.subheader("About")
    st.write("**GRE Vocabulary Master**")
    st.write("Version: 1.0.0")
    st.write("Total words in database:", sum(len(words) for words in vocab_groups.values()))
    st.write("Number of groups:", len(vocab_groups))
    st.write("Created with ❤️ using Streamlit")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6B7280;'>"
    "📚 GRE Vocabulary Master • Study Smarter, Not Harder • "
    f"<span id='word-count'>{sum(len(words) for words in vocab_groups.values())}</span> words to master"
    "</div>",
    unsafe_allow_html=True
)
