from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain.messages import SystemMessage,HumanMessage,AIMessage

load_dotenv()

models=ChatMistralAI(model="mistral-small-latest")

print("Choose Gym Trainer")
print("press 1 for Muscle Gain")
print("press 2 for Weight Loss")
print("press 3 for General Fitness")

choice=int(input("Tell your choice: "))

if choice==1:
    mode= """
    You are an AI Gym Trainer specialized in muscle gain.
    Help the user with workout guidance, exercises, sets, reps,
    rest periods, and general fitness advice for muscle building.
    Keep your answers simple and beginner-friendly.
    """
elif choice==2:
    mode="""
    You are an AI Gym Trainer specialized in weight loss.
    Help the user with workout guidance, exercises, sets, reps,
    rest periods, and general fitness advice for weight management.
    Keep your answers simple and beginner-friendly.
    """    
elif choice==3:
    mode="""
    You are an AI Gym Trainer specialized in general fitness.
    Help the user with workout guidance, exercises, sets, reps,
    rest periods, and general fitness advice.
    Keep your answers simple and beginner-friendly.
    """
message=[
    SystemMessage(content=mode)
]

print("------0 to Exit -------")
while True:
    prompt=input("You: ")
    message.append(HumanMessage(content=prompt))

    if prompt=='0':
        break
    response=models.invoke(message)
    message.append(AIMessage(content=response.content))

    print("Bot : ",response.content)
print(message)    