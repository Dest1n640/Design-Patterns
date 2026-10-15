import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, Response

from Src.Core.exception import ValidationException
from Src.Core.report_type import ReportType
from Src.Logics.report_factory import ReportFactory
from Src.Logics.settings_manager import SettingsManager
from Src.Logics.storage_manager import StorageManager

# Запуск: читает settings.json и формирует данные хранилища.
settings_manager = SettingsManager()
settings_manager.load()
StorageManager().start(settings_manager.settings)

app = FastAPI()


@app.get("/reports/{report_type}/{dish_name}")
def get_report(report_type: ReportType, dish_name: str) -> Response:
    """Возвращает отчёт по блюду из технологических карт: текст или байты."""
    dishes = [d for m in StorageManager().technological_maps for d in m.dishes]
    dish = next((d for d in dishes if d.name == dish_name), None)
    if dish is None:
        raise HTTPException(404, f"Блюдо '{dish_name}' не найдено")
    try:
        report = ReportFactory().create(report_type).build(dish)
    except ValidationException as ex:
        raise HTTPException(400, ex.message) from ex
    if report.binary:
        return Response(report.binary, media_type="application/octet-stream")
    return PlainTextResponse(report.text)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
