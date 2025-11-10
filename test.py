from google import genai

client = genai.Client()
myfile = client.files.upload(file=media / "requirements.txt")
file_name = myfile.name
print(file_name)  # "files/*"

myfile = client.files.get(name=file_name)
print(myfile)