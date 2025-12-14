from fastapi import APIRouter, UploadFile, File
from dishka.integrations.fastapi import FromDishka
from src.infrastructure.storage import ImageStorage

router = APIRouter()


@router.post("/upload-test")
async def upload_image(
    storage: FromDishka[ImageStorage], image: UploadFile = File(...)
):
    # .file - это файловый объект, который нужен cloudinary
    url = await storage.upload_file(image.file, folder="test_uploads")

    return {"url": url, "filename": image.filename}
