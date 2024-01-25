from fastapi.responses import HTMLResponse, RedirectResponse
from converttohtml import main as converttohtml
import uvicorn
from fastapi import FastAPI, File, UploadFile
import decryptor14
import decryptor15
from fastapi.staticfiles import StaticFiles
import random
import string
import os


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


app = FastAPI()
app.mount("/resources",
          StaticFiles(directory="converttohtml/resources"), name="resources")


@app.post("/upload")
async def upload_file(encrypted_file: UploadFile = File(...), key_file: UploadFile = File(...)):
    rand_path = generate_random_string(10)
    os.mkdir(f"converttohtml/resources/{rand_path}")
    os.mkdir(f"cache/{rand_path}")
    file_name = encrypted_file.filename
    key_file_name = key_file.filename
    if file_name.endswith("crypt14"):
        if key_file.filename == "key":
            # Save those files without reading them into memory
            with open(f"cache/{rand_path}/{file_name}", "wb") as file:
                file.write(encrypted_file.file.read())
            with open(f"cache/{rand_path}/{key_file_name}", "wb") as file:
                file.write(key_file.file.read())
            decryptor14.decrypt_14_db(
                f"cache/{rand_path}/{key_file_name}", f"cache/{rand_path}/{file_name}", f"cache/{rand_path}/decrypted.db")
            config = {
                'input': {
                    'msgstore_path': f"cache/{rand_path}/decrypted.db",
                    'use_wa_db': 'False',
                    'wa_path': f"cache/{rand_path}/decrypted.db"
                },
                'output': {
                    'export_html': 'True',
                    'html_output_path': f'converttohtml/resources/{rand_path}/index.html',
                    'export_txt': 'False',
                    'txt_output_directory_path': 'converttohtml/resources'
                }
            }
            converttohtml.main(config)
            return RedirectResponse(url=f"/resources/{rand_path}/index.html", status_code=302)
            return HTMLResponse(content=f"<script>window.location.href='/resources/{rand_path}/index.html'</script>", status_code=302)

    if file_name.endswith("crypt15"):
        if key_file.filename == "encrypted_backup.key":
            with open(f"cache/{rand_path}/{file_name}", "wb") as file:
                file.write(encrypted_file.file.read())
            with open(f"cache/{rand_path}/{key_file_name}", "wb") as file:
                file.write(key_file.file.read())
            decryptor15.decrypt_15_db(
                f"cache/{rand_path}/{key_file_name}", f"cache/{rand_path}/{file_name}", f"cache/{rand_path}/decrypted.db")
            config = {
                'input': {
                    'msgstore_path': f"cache/{rand_path}/decrypted.db",
                    'use_wa_db': 'False',
                    'wa_path': f"cache/{rand_path}/decrypted.db"
                },
                'output': {
                    'export_html': 'True',
                    'html_output_path': f'converttohtml/resources/{rand_path}/index.html',
                    'export_txt': 'False',
                    'txt_output_directory_path': 'converttohtml/resources'
                }
            }
            converttohtml.main(config)
            return RedirectResponse(url=f"/resources/{rand_path}/index.html", status_code=302)
            return HTMLResponse(content=f"<script>window.location.href='/resources/{rand_path}/index.html'</script>", status_code=302)


@app.get("/")
async def root():
    return HTMLResponse(content="""
                        <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Upload Form</title>
</head>
<body>
    <h2>File Upload Form</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <label for="encrypted_file">Select Encrypted File (.crypt14 or .crypt15):</label>
        <input type="file" name="encrypted_file" id="encrypted_file" required accept=".crypt14, .crypt15"><br>

        <label for="key_file">Select Key File:</label>
        <input type="file" name="key_file" id="key_file" required accept=".key"><br>

        <input type="submit" value="Upload and Convert">
    </form>
</body>
</html>

                        """, status_code=200)


@app.get("/reset")
def reset():
    if os.path.exists("cache"):
        list = os.listdir("cache")
        for i in list:
            if i != "index.html":
                os.system(f"rm -rf cache/{i}")
    return HTMLResponse(content="Done!", status_code=200)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True,)
