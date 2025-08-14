from deepface import DeepFace
import os
import gradio as gr
import configparser
base_dir = os.path.dirname(__file__)

def recognize(image):
    try:
        db_path = os.path.join(base_dir, "db")
        dfs = DeepFace.find(img_path=image, db_path=db_path)
        niks = niks = list(set(
            os.path.basename(os.path.dirname(element))
            for element in dfs[0]['identity'].values
        ))
        if len(niks) > 1:
            return {"success": False, "niks": niks, "info": "Identitas ganda"}
        return {"success": True, "niks": niks, "info": None}
    except Exception as e:
        return {"success": False, "niks": [], "info": str(e)}

def verify(image, nik):
    try:
        if not nik:
            raise ValueError("NIK tidak boleh kosong")
        db_path = os.path.join(base_dir, "db", nik)
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"NIK '{nik}' tidak terdaftar")
        first_image = None
        with os.scandir(db_path) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    first_image = entry.path
                    break
        if not first_image:
            raise FileNotFoundError(f"Database NIK '{nik}' kosong")
        dfs = DeepFace.verify(img1_path=image, img2_path=first_image)
        return {"success": dfs['verified'], "info": None}
    except Exception as e:
        return {"success": False, "info": str(e)}

with gr.Blocks() as app:
    img = gr.Image(label="Name")
    nik = gr.Textbox(label="NIK")
    rec = gr.Button("Recognize")
    ver = gr.Button("Verify")
    out = gr.Textbox(label="Info")
    rec.click(fn=recognize, inputs=img, outputs=out, api_name="recognize")
    ver.click(fn=verify, inputs=[img,nik], outputs=out, api_name="verify")

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config_path = os.path.join(base_dir, "config.ini")
    server_name = "0.0.0.0"
    server_port = 7860
    if os.path.exists(config_path):
        config.read(config_path)
        server_name = config.get("webui", "host", fallback="0.0.0.0")
        server_port = config.getint("webui", "port", fallback=7860)
    app.launch(server_name=server_name, server_port=server_port)