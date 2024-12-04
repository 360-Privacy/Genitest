import threading
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QPushButton, QVBoxLayout, QWidget
import os
import sys
import time
from openai import OpenAI





CONTEXT_FILE = os.getenv("CONTEXT_FILE")

sys.stderr = open(os.devnull, 'w')

base_context = (
    """This GPT's goal is to help users create Python unit tests by analyzing the code provided in the uploaded files and generating appropriate unit tests for the functions and methods in those files. It will ensure the tests are comprehensive and follow best practices for unit testing in Python. The GPT should only create unit tests and not modify the original code unless specified by the user. It should follow the pytest framework standards and avoid using other testing libraries unless specified by the user. The tests should be up-to-date and follow best practices for Python unit testing. The GPT will clearly explain the generated tests, ensuring they cover various scenarios, including edge cases, and are easy to understand and maintain. The emphasis will be on testing the unhappy paths, focusing on finding all possible bad outcomes and assessing the likelihood of their occurrence, rather than on preferred outcomes.

Upon receiving a file from the user, the GPT will go through the following list of checks before generating any code:
1. Review the Code:
   - Read through the code to understand its functionality.
   - Identify the inputs, outputs, and the main logic.
2. Understand Dependencies:
   - Identify any external dependencies (e.g., databases, APIs, services).
   - Determine how these dependencies can be mocked or stubbed.
3. Create or identify test data that will be used in your tests:
   - Ensure you have data for typical, edge, and error cases.
4. Define Test Objectives:
   - Clearly define what you aim to achieve with your tests (e.g., verify function outputs, ensure error handling).
5. Write down a list of test cases covering all possible scenarios, including:
   - Positive cases
   - Edge cases
   - Negative cases.
6. Determine Metrics:
   - Determine what metrics you will use to evaluate the success of the tests (e.g., code coverage, pass/fail rate).
7. Start with Simple Tests:
   - Begin by writing simple tests for the most straightforward functions.
   - Verify that basic inputs produce expected outputs.
8. Incrementally Increase Complexity:
   - Gradually write more complex tests covering edge cases and error conditions.
9. Use Assertions:
   - Use assertions to verify that the actual output matches the expected output.
   - Ensure assertions are specific and provide meaningful feedback when they fail.
10. Identify What to Mock:
    - Determine which external dependencies need to be mocked (e.g., network calls, database queries).
11. Create Mocks:
    - Use mocking libraries or the testing framework's built-in features to create mocks.
    - Ensure mocks return expected results for various inputs.
12. Test with Mocks:
    - Write tests that use the mocks instead of real dependencies.
    - Verify that the code interacts with the mocks correctly.

After generating the tests, the GPT will review the test code:
1. Review Test Code:
   - Ensure your test code is clean and follows best practices.
   - Refactor tests to remove duplication and improve readability.
2. Optimize for Performance:
   - Ensure tests run efficiently and do not take too long to execute.
   - Use setup and teardown methods to optimize repetitive tasks.

If the user does not specify, it will default to creating basic tests covering typical use cases and edge cases. If the GPT detects any security concerns or optimization issues in the provided code, it will ask the user if they would like recommendations after building the tests. If the user agrees, the GPT will offer to rebuild the original code to be more streamlined and up to Python standards, with a focus on security as the highest priority. It will maintain a helpful and professional tone, being concise and clear in explanations. The GPT will communicate in a casual and friendly manner, explaining in detail (Barney style) all the tests that have been created, preferably right after generating the tests.  Use Setup, Execute and verify terminology for the comments.  Include the class name in lowercase snake case conventions when naming each function.  Explain each test case in the comments of the code.
When reviewing and creating output is absolutely crucial that you folllow these instructions:

Make sure the class name for the tests is "Test"  then the name of the class following immediately after.  Include the @pytest.mark.asyncio above the class initialization.  Put the tests for all this code, in one copiable python code block.""",
)


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class SaveTest(QMainWindow):
    def __init__(self):

        super().__init__()
        self.client = client
        try:  # Load the context file
            with open(CONTEXT_FILE, "r") as f:
                self.context = f.read()

        except FileNotFoundError:
            self.context = base_context[0]
        self.conversation_log = [{"role": "user", "content": self.context}]
        selected_files = self.open_multiple_files()
        start_text = "Below are the files you need to analyze."
        # Print the selected file paths
        for file in selected_files:
            with open(file, "r") as f:
                data = f.read()
                name = file.split("/")[-1]
                start_text += f"\n{name}: \n\n```\n{data}\n```\n\n"
        markdown = self.query_chatgpt(start_text)
        self.text_to_copy = ""
        count = 0
        for text_portion in range(1, len(markdown.split("```"))):
            if text_portion % 2 == 1:
                count += 1
                portion = markdown.split("```")[text_portion]
                portion_pieces = portion.splitlines()
                final_portion = "\n".join(portion_pieces[1:])
                self.text_to_copy += final_portion + "\n\n\n"

    def spinner(self):
        while True:
            for cursor in "|/-\\":
                yield cursor

    def show_spinner(self, spinner_gen):
        while not spinner_done:
            print(f"\rGenerating Unit Tests... {next(spinner_gen)}", end="", flush=True)
            time.sleep(0.1)
        print("\r" + " " * 15, end="\r")

    def query_chatgpt(self, prompt):
        global spinner_done
        spinner_done = False
        spinner_gen = self.spinner()
        spinner_thread = threading.Thread(target=self.show_spinner, args=(spinner_gen,))
        spinner_thread.start()
        self.conversation_log.append({"role": "user", "content": prompt})
        chat_completion = self.client.chat.completions.create(
            messages=self.conversation_log,
            model="o1-mini",
        )
        spinner_done = True
        spinner_thread.join()
        return chat_completion.choices[0].message.content

    def open_multiple_files(self):
        files, _ = QFileDialog.getOpenFileNames(None, "Select Files")
        return files

    def show_save_dialog(self):
        # Open a Save File dialog
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,  # Parent widget
            "Save File",  # Dialog title
            "",  # Default directory or file name
            "All Files (*);;Text Files (*.txt);;Python Files (*.py)",  # File types
            options=options,
        )
        if file_path:
            return file_path, self.text_to_copy
        return None, None


# Get the selected files
def main():
    app = QApplication([])
    window = SaveTest()
    file, content = window.show_save_dialog()
    if file and content:
        with open(file, "w") as f:
            f.write(content)


if __name__ == "__main__":
    main()
