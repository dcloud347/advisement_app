from openai import OpenAI


class OpenAITools:

    @staticmethod
    def get_advisement(message: str, messages: list):
        client = OpenAI()
        messages.append({"role": "user", "content": message})
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        returned_message = completion.choices[0].message.content
        role = completion.choices[0].message.role
        messages.append({"role": role, "content": returned_message})
        return returned_message, role


if __name__ == "__main__":
    messages = [{"role": "system", "content": "You are now an expert in medication."}]
    print(OpenAITools.get_advisement("beclomethasone dipropionate 40mcg aerosol 2 puffs twice daily", messages))
