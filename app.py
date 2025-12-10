import os
import streamlit as st
import pandas as pd
from src.clean_food_matcher import CleanFoodMatcher
from src.llm_summarizer import NutritionSummarizer
from src.meal_recommender import MealRecommender
from src.nhanes_analyzer import NHANESAnalyzer
from src.clinical_parser import ClinicalNotesParser

# Page config
st.set_page_config(
    page_title="Daily Nutrition Analyzer",
    page_icon="🥗",
    layout="wide"
)

# Initialize components
@st.cache_resource
def load_food_matcher():
    return CleanFoodMatcher('data/nutrition_db_clean.csv')

@st.cache_resource  
def load_summarizer():
    return NutritionSummarizer()

@st.cache_resource
def load_recommender():
    return MealRecommender()

@st.cache_resource
def load_nhanes_analyzer():
    return NHANESAnalyzer()

@st.cache_resource
def load_clinical_parser():
    return ClinicalNotesParser()



def calculate_totals(nutrition_data):
    """Calculate daily totals from nutrition data"""
    totals = {
        'calories': sum(item['calories'] for item in nutrition_data),
        'protein': sum(item['protein'] for item in nutrition_data),
        'carbs': sum(item['carbs'] for item in nutrition_data),
        'fat': sum(item['fat'] for item in nutrition_data)
    }
    return totals

def main():
    st.title("🥗 Daily Nutrition Analyzer")
    st.markdown("*Paste or type what you ate today and receive a nutrition breakdown.*")
    
    # Load food matcher
    food_matcher = load_food_matcher()
    
    # Initialize session state
    if 'analyzed' not in st.session_state:
        st.session_state.analyzed = False
    
    # User profile section
    with st.sidebar:
        st.markdown("### 👤 Your Profile")
        target_calories = st.slider("Daily Calorie Target", 1200, 3000, 2000, 100)
        dietary_pref = st.selectbox("Dietary Preference", ["No restrictions", "Vegetarian", "Vegan", "Low-carb", "High-protein"])
        
        # Demographics for NHANES comparison
        st.markdown("### 📊 Demographics (Optional)")
        age = st.number_input("Age", 18, 100, 30)
        gender = st.selectbox("Gender", ["Male", "Female"])
        

        
        # Clinical notes section
        st.markdown("### 🏥 Clinical Notes (Optional)")
        clinical_notes = st.text_area(
            "Paste clinical nutrition notes:",
            placeholder="e.g., Patient advised 1800 calories daily, diabetic diet, limit sodium to 2000mg...",
            height=100
        )
    
    # Input section
    st.subheader("📝 Enter Your Daily Meals")
    
    example_text = """Breakfast: 2 idlis with coconut chutney.
Lunch: 1 cup rice, dal, curd.
Dinner: 2 chapatis, mixed vegetable.
Snack: 1 banana."""
    
    user_input = st.text_area(
        "Type your meals here:",
        value=st.session_state.get('user_input', ''),
        placeholder=example_text,
        height=150,
        help="Include meals like: Breakfast: 2 idlis, coconut chutney. Lunch: rice, dal, curd...",
        key='user_input'
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        analyze_button = st.button("🔍 Analyze", type="primary")
    
    with col2:
        if st.button("🔄 Clear"):
            st.session_state.analyzed = False
            # Clear the text input by using a key and resetting it
            if 'user_input' in st.session_state:
                del st.session_state.user_input
            st.rerun()
    
    # Analysis section
    if analyze_button and user_input.strip():
        with st.spinner("Analyzing your nutrition..."):
            summarizer = load_summarizer()
            
            # Extract foods using clean matcher
            foods = food_matcher.extract_foods_with_quantities(user_input)
            
            if not foods:
                st.error("No recognizable foods found. Try simpler names like: toast, chicken, apple, rice.")
                return
            
            nutrition_data, unknown_foods = food_matcher.get_nutrition_data(foods)
            
            if not nutrition_data:
                st.error("None of the foods could be found in our database. Please try common foods like rice, dal, chapati, etc.")
                return
            
            # Calculate totals
            totals = calculate_totals(nutrition_data)
            
            # Generate summary with demographic info
            summary, ai_method, evidence_sources = summarizer.generate_summary(nutrition_data, totals, age, gender)
            
            # Generate meal recommendations
            recommender = load_recommender()
            gaps = recommender.analyze_gaps(totals, target_calories)
            recommendations = recommender.get_food_recommendations(gaps)
            meal_suggestions = recommender.generate_meal_plan_suggestions(gaps, recommendations)
            
            # NHANES population comparison
            nhanes_analyzer = load_nhanes_analyzer()
            demographic_comparison = nhanes_analyzer.get_demographic_comparison(totals, age, gender)
            population_insights = nhanes_analyzer.generate_population_insights(demographic_comparison)
            risk_assessment = nhanes_analyzer.get_risk_assessment(demographic_comparison, totals)
            
            # Clinical notes analysis
            clinical_summary = ""
            if clinical_notes.strip():
                clinical_parser = load_clinical_parser()
                parsed_clinical = clinical_parser.parse_clinical_notes(clinical_notes)
                clinical_summary = clinical_parser.generate_clinical_summary(parsed_clinical, totals)
            

            
            st.session_state.analyzed = True
            st.session_state.nutrition_data = nutrition_data
            st.session_state.totals = totals
            st.session_state.summary = summary
            st.session_state.ai_method = ai_method
            st.session_state.unknown_foods = unknown_foods
            st.session_state.recommendations = recommendations
            st.session_state.meal_suggestions = meal_suggestions
            st.session_state.target_calories = target_calories
            st.session_state.evidence_sources = evidence_sources
            st.session_state.demographic_comparison = demographic_comparison
            st.session_state.population_insights = population_insights
            st.session_state.risk_assessment = risk_assessment
            st.session_state.clinical_summary = clinical_summary
            st.session_state.age = age
            st.session_state.gender = gender
    
    # Display results
    if st.session_state.analyzed:
        st.subheader("📊 Nutrition Analysis Results")
        
        # Daily totals - prominent display
        st.markdown("### 🎯 Daily Totals")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Calories", f"{st.session_state.totals['calories']:.0f}")
        with col2:
            st.metric("Protein", f"{st.session_state.totals['protein']:.2f}g")
        with col3:
            st.metric("Carbs", f"{st.session_state.totals['carbs']:.2f}g")
        with col4:
            st.metric("Fat", f"{st.session_state.totals['fat']:.2f}g")
        
        # Detailed breakdown
        st.markdown("### 📋 Food Breakdown")
        df = pd.DataFrame(st.session_state.nutrition_data)
        # Select only the columns we want to display
        display_df = df[['food', 'quantity', 'calories', 'protein', 'carbs', 'fat']]
        display_df.columns = ['Food', 'Quantity', 'Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)']
        st.dataframe(display_df, use_container_width=True)
        
        # LLM Summary with RAG
        st.markdown("### 💡 Evidence-Based Nutrition Insights")
        st.info(st.session_state.summary)
        st.caption(f"Generated using: {st.session_state.ai_method}")
        
        # Meal Recommendations
        st.markdown("### 🍽️ Personalized Meal Recommendations")
        if st.session_state.recommendations:
            st.success("Based on your nutrition gaps, here are specific food suggestions:")
            st.markdown(st.session_state.meal_suggestions)
            
            # Show detailed recommendations in expandable section
            with st.expander("📋 Detailed Nutrition Impact"):
                rec_df = pd.DataFrame([
                    {
                        'Food': f"{rec['quantity']} {rec['unit']} {rec['food']}",
                        'Calories': f"+{rec['nutrition']['calories']:.0f}",
                        'Protein': f"+{rec['nutrition']['protein']:.1f}g",
                        'Reason': rec['reason']
                    }
                    for rec in st.session_state.recommendations
                ])
                st.dataframe(rec_df, use_container_width=True)
        else:
            st.info("🎯 Your nutrition looks well balanced for your target calories!")
        
        # Show target vs actual
        with st.expander("🎯 Target vs Actual Comparison"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Target Calories", f"{st.session_state.target_calories}")
                st.metric("Actual Calories", f"{st.session_state.totals['calories']:.0f}", 
                         f"{st.session_state.totals['calories'] - st.session_state.target_calories:+.0f}")
            with col2:
                protein_target = (st.session_state.target_calories * 0.20) / 4
                st.metric("Target Protein", f"{protein_target:.0f}g")
                st.metric("Actual Protein", f"{st.session_state.totals['protein']:.1f}g",
                         f"{st.session_state.totals['protein'] - protein_target:+.1f}g")
        
        # Population Health Insights
        st.markdown("### 📊 Population Health Comparison")
        
        # Add explanation
        with st.expander("ℹ️ What is Population Health Comparison?"):
            st.markdown("""
            **Population Health Comparison** uses data from the **NHANES (National Health and Nutrition Examination Survey)** 
            to compare your nutrition intake with thousands of people in your demographic group.
            
            **How it works:**
            - Compares your intake to people of same age group and gender
            - Shows percentiles (50th = average, 75th = above average)
            - Identifies potential health risks based on population patterns
            - Uses real survey data from CDC/NHANES
            
            **Sample sizes:** Based on 1,000-1,500 people per demographic group
            """)
        
        if hasattr(st.session_state, 'population_insights') and st.session_state.population_insights:
            st.info(f"Compared to {st.session_state.gender.lower()}s aged {st.session_state.age} in NHANES survey:")
            for insight in st.session_state.population_insights:
                st.markdown(f"• {insight}")
            
            # Risk assessment
            risk = st.session_state.risk_assessment
            if risk['risk_level'] == 'high':
                st.error(f"⚠️ High Risk Profile: {', '.join(risk['factors'])}")
            elif risk['risk_level'] == 'moderate':
                st.warning(f"🟡 Moderate Risk: {', '.join(risk['factors'])}")
            else:
                st.success("✅ Low risk profile based on population data")
        
        # Clinical Analysis
        if hasattr(st.session_state, 'clinical_summary') and st.session_state.clinical_summary:
            st.markdown("### 🏥 Clinical Analysis")
            st.markdown(st.session_state.clinical_summary)
        
        # Show evidence sources
        with st.expander("📚 Nutrition Guidelines Used"):
            st.markdown("""
            **Nutrition recommendations based on:**
            - WHO (World Health Organization) dietary guidelines
            - USDA Dietary Guidelines for Americans
            - Clinical nutrition research and best practices
            - Population health data from NHANES surveys
            
            *Note: This analysis provides general nutrition information and should not replace professional medical advice.*
            """)
        
        # Unknown foods
        if st.session_state.unknown_foods:
            st.markdown("### ❓ Items Not Found")
            st.warning(f"Could not find nutrition data for: {', '.join(st.session_state.unknown_foods)}")
            st.caption("Try using more common food names or check spelling.")
    
    elif analyze_button:
        st.error("Please enter some food items to analyze.")
    
        st.markdown("### ℹ️ How to Use")
        st.markdown("""
        1. **Set your target** calories above
        2. **Enter your meals** in the text box
        3. **Include quantities** when possible (e.g., "2 idlis", "1 cup rice")
        4. **Click Analyze** to get personalized recommendations
        """)
        
        st.markdown("### 🥘 Supported Foods")
        st.caption("rice, bread, pasta, oatmeal, egg, chicken breast, salmon, beef, tofu, yogurt, milk, cheese, banana, apple, broccoli, spinach, carrot, potato, avocado, almonds, olive oil, butter")
        
        st.markdown("### 🎯 Features")
        st.caption("• Personalized recommendations\n• Population health comparison\n• Clinical notes analysis\n• Evidence-based insights\n• Research evaluation metrics\n• Expert validation interface")
        
        st.markdown("### 📈 Research Metrics")
        st.caption("• ROUGE/BLEU text quality\n• Evidence grounding scores\n• Recommendation accuracy\n• Expert validation ratings")

if __name__ == "__main__":
    main()