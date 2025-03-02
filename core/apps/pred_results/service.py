


from abc import abstractmethod
from dataclasses import dataclass

import requests

from core.apps.customers.entities.customers import CustomerEntity
from core.apps.pred_results.entity import Pred_resultsEntity
from core.apps.pred_results.models import Pred_results
from core.core.settings.main import env
import requests
from io import BytesIO
@dataclass
class BasePredResults:
    @abstractmethod
    def save_pred_result(
        self,
        customer: CustomerEntity,
        predres: Pred_resultsEntity,
    ) -> Pred_resultsEntity:
        ...
    @abstractmethod        
    def get_pred_results(
        self, 
        customer: CustomerEntity
    ) -> list[Pred_resultsEntity]:
        ...
    @abstractmethod
    def get_better_pred_results(
        self,
        image_file_path: str
    ) -> dict[str, any]:
        ...

class ORMPredResults(BasePredResults):
    def save_pred_result(
        self,
        customer: CustomerEntity,
        predres: Pred_resultsEntity,
    ) -> Pred_resultsEntity:
        predresDTO: Pred_results = Pred_results.from_entity(
            pred_results=predres,
            customer=customer,
        )
        predresDTO.save()
        return predresDTO.to_entity()
    def get_pred_results(
        self, 
        customer: CustomerEntity
    ) -> list[Pred_resultsEntity]:
        predres_dtos = Pred_results.objects.filter(customer_id=customer.id)
        return [predres_dto.to_entity() for predres_dto in predres_dtos]


    def get_better_pred_results(self,image_file_path: str) -> dict[str, any]:
        try:
            with open(image_file_path, "rb") as f:
                image_bytes = f.read()
        except FileNotFoundError:
            print(f"Файл {image_file_path} не найден. Проверьте путь.")
            return None

        files_skin = {"image_file": BytesIO(image_bytes)}

        skin_url = "https://api-us.faceplusplus.com/facepp/v1/skinanalyze"

        skin_data = {
            "api_key": env('API_key_FACE'),
            "api_secret": env('API_secret_FACE')
        }

        skin_response = None

        try:
            skin_resp = requests.post(skin_url, data=skin_data, files=files_skin)
            skin_resp.raise_for_status()
            skin_response = skin_resp.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса для skin analyze: {e}")

        return skin_response
