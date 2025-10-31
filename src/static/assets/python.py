import random
name = input("What is your name?\n")
print("hello ", name)
def count (number):
    n=1
    while n<= number:
        print (n)
        n= n+1
        
# myNumber.py
# This game uses a home made function import random
# Think of a number
computer_number = random.randint(1, 100)
# Create the function is_same()
def is_same(target, number):
    if target == number: result="Win"
    elif target > number: result="Low"
    else:
        result="High"
    return result # Start the game
print("Hello.\nI have thought of a number between 1 and 100.")
# Collect the user’s guess as an integer
guess = int(input("Can you guess it? "))
# Use our function
higher_or_lower = is_same(computer_number, guess)
# Run the game until the user is correct
while higher_or_lower != "Win":
    if higher_or_lower == "Low":
        guess = int(input("Sorry, you are too low. Try again. "))
    else:
            guess = int(input("Sorry, you are too high. Try again. "))
    higher_or_lower = is_same(computer_number, guess)
# End the game
input("Correct!\nWell Done\n\n\nPress RETURN to exit.")
