from pipliner import pipliner
from memory import Memory
from state import State

memory = Memory()


# hy i want to study abroad now i am from pakistan and remember that i do not have any bank statement and any money for payment i only have a bacholar degree with 3.10 cgpa and also i do not have nay ielate certificate and my study is about the computer science in artificial intelligenceand also a backend developer now find the best choise for me


if __name__ == "__main__":
    while True:
        user_input = input("Ask Anything : ")
        # memory.add_memory(user_input, "human")

        # stack.append({"type": "input", "content": user_input})
        if user_input == "Exit" or user_input.lower() == "exit":
            break
        state = State(user_input=user_input)

        response = pipliner(state)
        # response = pipliner(user_input, state.user_input, memory.get_memory())
        print(response)
