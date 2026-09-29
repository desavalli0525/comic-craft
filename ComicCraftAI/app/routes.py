from pathlib import Path

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    FileResponse,
)

from fastapi.templating import Jinja2Templates

from app.schemas import PromptRequest

from app.generation_service import (
    generate_comic,
)

from app.image_generator import (
    generate_image,
)


BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(
        BASE_DIR / "templates"
    )
)

router = APIRouter()


# --------------------------------------
# HOME
# --------------------------------------

@router.get(
    "/",
    response_class=HTMLResponse,
)
async def home(
    request: Request,
):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


# --------------------------------------
# FORM GENERATION
# --------------------------------------

@router.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate(
    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...),
):

    try:

        payload = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        comic_id, layout, pdf_path = (
            generate_comic(payload)
        )

        pdf_url = (
            "/static/exports/"
            + Path(pdf_path).name
        )

        return templates.TemplateResponse(
            "comic_preview.html",
            {
                "request": request,
                "layout": layout,
                "comic_id": comic_id,
                "pdf_url": pdf_url,
            },
        )

    except Exception as exc:

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error":
                    "Comic generation failed: "
                    + str(exc),
            },
            status_code=500,
        )


# --------------------------------------
# JSON API
# --------------------------------------

@router.post(
    "/generate-comic/json"
)
async def generate_json(
    payload: PromptRequest,
):

    try:

        comic_id, layout, pdf_path = (
            generate_comic(payload)
        )

        return JSONResponse(
            {
                "comic_id": comic_id,

                "panels": layout,

                "pdf_url":
                    "/static/exports/"
                    + Path(pdf_path).name,
            }
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# --------------------------------------
# EXPORT SUCCESS
# --------------------------------------

@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(
    request: Request,
    pdf: str | None = None,
):

    return templates.TemplateResponse(
        "export_success.html",
        {
            "request": request,
            "pdf": pdf,
        },
    )


# --------------------------------------
# PDF DOWNLOAD
# --------------------------------------

@router.get(
    "/download/{filename}"
)
async def download(
    filename: str,
):

    path = (
        BASE_DIR
        / "static"
        / "exports"
        / filename
    )

    if (
        not path.exists()
        or path.suffix.lower() != ".pdf"
    ):

        raise HTTPException(
            status_code=404,
            detail="PDF not found",
        )

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=path.name,
    )


# --------------------------------------
# IMAGE TEST
# --------------------------------------

@router.get(
    "/test-image"
)
async def test_image(
    prompt: str =
        "A brave fox exploring "
        "an enchanted forest, "
        "comic book style",
):

    try:

        image_path = generate_image(
            prompt,
            0,
            "test-image",
        )

        return {
            "image_url":
                "/static/panels/"
                + Path(image_path).name
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )