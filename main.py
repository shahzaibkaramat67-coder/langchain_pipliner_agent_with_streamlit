from pipliner import pipliner
from memory import Memory
from state import State

memory = Memory()


# hy i want to study abroad now i am from pakistan and remember that i do not have any bank statement and any money for payment i only have a bacholar degree with 3.10 cgpa and also i do not have nay ielate certificate and my study is about the computer science in artificial intelligenceand also a backend developer now find the best choise for me


# from state import State
# from pipliner import pipliner
from rich import print


def main():
    print("[bold violet]AI Agent Orchestrator[/bold violet]")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("Ask Anything: ").strip()

            if user_input.lower() == "exit":
                print("Goodbye!")
                break

            if not user_input:
                continue

            state = State(user_input=user_input)
            response = pipliner(state)

            print("\n[bold green]Final Answer:[/bold green]")
            print(response)
            print("\n" + "-" * 60 + "\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as error:
            print(f"[bold red]Error:[/bold red] {error}")


if __name__ == "__main__":
    main()
