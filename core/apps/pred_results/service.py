


from abc import abstractmethod
from dataclasses import dataclass

import requests

from core.apps.customers.entities.customers import CustomerEntity
from core.apps.pred_results.entity import Pred_resultsEntity
from core.apps.pred_results.models import Pred_results
from core.core.settings.main import env

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
    def get_better_pred_results(self, image_file_path: str) -> dict[str, any]:
        url = "https://api-us.faceplusplus.com/facepp/v1/skinanalyze"
        data = {
            "api_key": env('API_key_FACE'),
            "api_secret": env('API_secret_FACE')
        }
        files = None
        if image_file_path:
            try:
                files = {"image_file": open(image_file_path, "rb")}
            except FileNotFoundError:
                print(f"Файл {image_file_path} не найден. Проверьте путь.")
                return None
        try:
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()  
            return response.json()  
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return None
        finally:
            if files and "image_file" in files:
                files["image_file"].close()