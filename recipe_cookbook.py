#!/usr/bin/env python3
"""
AI Recipe Cookbook using Gemini API
Takes console input for ingredients and generates recipes
"""

import google.generativeai as genai
import os
import json
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class RecipeCookbook:
    def __init__(self, api_key: str = None):
        """
        Initialize the Recipe Cookbook with Gemini API
        
        Args:
            api_key: Your Gemini API key. If None, will look for GEMINI_API_KEY environment variable
        """
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("Please provide a Gemini API key or set GEMINI_API_KEY environment variable")
        
        genai.configure(api_key=api_key)
        # Use only free Gemini models
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        except:
            try:
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except:
                try:
                    self.model = genai.GenerativeModel('models/gemini-1.5-flash')
                except:
                    raise ValueError("Could not initialize free Gemini model. Please check your API key.")
        
        # Create recipes folder if it doesn't exist
        self.recipes_folder = "generated_recipes"
        os.makedirs(self.recipes_folder, exist_ok=True)
    
    def get_ingredients_from_user(self) -> List[str]:
        """
        Get ingredients from user input
        
        Returns:
            List of ingredients
        """
        print("\n=== AI Recipe Cookbook ===")
        print("Enter your ingredients (one per line, press Enter twice when done):")
        
        ingredients = []
        while True:
            ingredient = input("Ingredient: ").strip()
            if ingredient == "":
                if ingredients:
                    break
                else:
                    print("Please enter at least one ingredient.")
            else:
                ingredients.append(ingredient)
        
        return ingredients
    
    def generate_recipe_prompt(self, ingredients: List[str], dietary_restrictions: str = "", cuisine_type: str = "") -> str:
        """
        Generate a detailed prompt for recipe creation
        
        Args:
            ingredients: List of available ingredients
            dietary_restrictions: Any dietary restrictions
            cuisine_type: Preferred cuisine type
            
        Returns:
            Formatted prompt string
        """
        ingredients_str = ", ".join(ingredients)
        
        prompt = f"""
        Create a detailed recipe using the following ingredients: {ingredients_str}
        
        Additional preferences:
        - Dietary restrictions: {dietary_restrictions if dietary_restrictions else "None"}
        - Cuisine type: {cuisine_type if cuisine_type else "Any"}
        
        Please provide:
        1. Recipe name
        2. Cooking time (prep + cook)
        3. Servings
        4. Complete ingredients list (including quantities and any additional ingredients needed)
        5. Step-by-step cooking instructions
        6. Difficulty level (Easy/Medium/Hard)
        7. Nutritional highlights
        8. Tips for best results
        
        Make the recipe practical and delicious. If some common pantry staples (salt, pepper, oil, etc.) are needed but not listed, include them in the ingredients with quantities.
        
        Format the response in a clear, organized manner.
        """
        
        return prompt
    
    def generate_recipe(self, ingredients: List[str], dietary_restrictions: str = "", cuisine_type: str = "") -> Dict:
        """
        Generate a recipe using Gemini API
        
        Args:
            ingredients: List of available ingredients
            dietary_restrictions: Any dietary restrictions
            cuisine_type: Preferred cuisine type
            
        Returns:
            Dictionary containing recipe information
        """
        try:
            prompt = self.generate_recipe_prompt(ingredients, dietary_restrictions, cuisine_type)
            
            print("\n🍳 Generating recipe with AI...")
            response = self.model.generate_content(prompt)
            
            recipe_data = {
                "timestamp": datetime.now().isoformat(),
                "input_ingredients": ingredients,
                "dietary_restrictions": dietary_restrictions,
                "cuisine_type": cuisine_type,
                "generated_recipe": response.text,
                "status": "success"
            }
            
            return recipe_data
            
        except Exception as e:
            print(f"❌ Error generating recipe: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "input_ingredients": ingredients,
                "error": str(e),
                "status": "error"
            }
    
    def save_recipe(self, recipe_data: Dict) -> str:
        """
        Save recipe to a file
        
        Args:
            recipe_data: Recipe data dictionary
            
        Returns:
            Filename of saved recipe
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recipe_{timestamp}.txt"
        filepath = os.path.join(self.recipes_folder, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=== AI Generated Recipe ===\n\n")
                f.write(f"Generated on: {recipe_data['timestamp']}\n")
                f.write(f"Input ingredients: {', '.join(recipe_data['input_ingredients'])}\n")
                if recipe_data.get('dietary_restrictions'):
                    f.write(f"Dietary restrictions: {recipe_data['dietary_restrictions']}\n")
                if recipe_data.get('cuisine_type'):
                    f.write(f"Cuisine type: {recipe_data['cuisine_type']}\n")
                f.write("\n" + "="*50 + "\n\n")
                
                if recipe_data['status'] == 'success':
                    f.write(recipe_data['generated_recipe'])
                else:
                    f.write(f"Error: {recipe_data['error']}")
            
            print(f"📁 Recipe saved to: {filepath}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving recipe: {str(e)}")
            return ""
    
    def get_additional_preferences(self) -> tuple:
        """
        Get additional preferences from user
        
        Returns:
            Tuple of (dietary_restrictions, cuisine_type)
        """
        print("\n--- Additional Preferences (optional) ---")
        dietary = input("Any dietary restrictions? (vegetarian, vegan, gluten-free, etc.): ").strip()
        cuisine = input("Preferred cuisine type? (Italian, Indian, Mexican, etc.): ").strip()
        
        return dietary, cuisine
    
    def display_recipe(self, recipe_data: Dict):
        """
        Display the generated recipe in console
        
        Args:
            recipe_data: Recipe data dictionary
        """
        print("\n" + "="*60)
        print("🍽️  YOUR GENERATED RECIPE")
        print("="*60)
        
        if recipe_data['status'] == 'success':
            print(recipe_data['generated_recipe'])
        else:
            print(f"❌ Error: {recipe_data['error']}")
        
        print("="*60)
    
    def run_interactive_mode(self):
        """
        Run the cookbook in interactive mode
        """
        print("🍳 Welcome to AI Recipe Cookbook!")
        print("Generate recipes from your ingredients using Google's Gemini AI")
        
        while True:
            try:
                # Get ingredients from user
                ingredients = self.get_ingredients_from_user()
                
                # Get additional preferences
                dietary_restrictions, cuisine_type = self.get_additional_preferences()
                
                # Generate recipe
                recipe_data = self.generate_recipe(ingredients, dietary_restrictions, cuisine_type)
                
                # Display recipe
                self.display_recipe(recipe_data)
                
                # Save recipe
                if recipe_data['status'] == 'success':
                    save_option = input("\n💾 Save this recipe? (y/n): ").lower().strip()
                    if save_option in ['y', 'yes']:
                        self.save_recipe(recipe_data)
                
                # Continue or exit
                print("\n" + "-"*40)
                continue_option = input("🔄 Generate another recipe? (y/n): ").lower().strip()
                if continue_option not in ['y', 'yes']:
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Thanks for using AI Recipe Cookbook!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                continue
        
        print("Happy cooking! 🍳✨")

def main():
    """
    Main function to run the recipe cookbook
    """
    try:
        # You can either:
        # 1. Set your API key as environment variable: export GEMINI_API_KEY="your_api_key_here"
        # 2. Or pass it directly (not recommended for production):
        # cookbook = RecipeCookbook(api_key="your_api_key_here")
        
        cookbook = RecipeCookbook()  # Uses environment variable
        cookbook.run_interactive_mode()
        
    except ValueError as e:
        print(f"❌ Configuration Error: {str(e)}")
        print("\nTo fix this:")
        print("1. Get your Gemini API key from: https://makersuite.google.com/app/apikey")
        print("2. Set it as environment variable: export GEMINI_API_KEY='your_api_key_here'")
        print("3. Or modify the code to pass the API key directly")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()