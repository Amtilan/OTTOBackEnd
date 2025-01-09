from dataclasses import dataclass, field
import typing_extensions as typing
import google.generativeai as genai
import json
from typing import List, Optional
from core.apps.pred_results.service import BasePredResults, ORMPredResults
from core.core.settings.main import env


@dataclass
class ProductRecommendation(typing.TypedDict):
    title: str


@dataclass
class RecommendationGenerator:
    catalog_file: str = field(default='combined.json', init=False)
    api_key: str = field(default=env('GOOGLE_API_KEY'), init=False)
    model_name: str = field(default=env('MODEL_NAME'), init=False)
    face_path: str = field(default=None)
    product_catalog: Optional[List[dict]] = field(default=None, init=False)
    recommendations: Optional[List[dict]] = field(default=None, init=False)
    pred_results: BasePredResults = field(default=ORMPredResults, init=True)
    def __post_init__(self):
        self._validate_api_key()
        self._configure_gemini()
        self._load_data()
        self.recommendations = self._generate_recommendations()

    def _validate_api_key(self) -> None:
        if not self.api_key:
            raise EnvironmentError(
                "Необходимо установить переменную окружения GOOGLE_API_KEY "
                "со значением вашего Gemini API ключа."
            )

    def _configure_gemini(self) -> None:
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def _load_data(self) -> None:
        self.product_catalog = self._load_json(self.catalog_file)

    @staticmethod
    def _load_json(file_path: str) -> dict:
        """Загрузка JSON-данных из файла."""
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _search_product_by_title(self, title: str) -> Optional[dict]:
        for product in self.product_catalog:
            if product.get("title") == title:
                return product
        return None
    def _generate_recommendations(self) -> List[dict]:
        analysis_results = self.pred_results.get_better_pred_results(image_file_path=self.face_path)
        if not analysis_results:
            analysis_results = {}
        prompt = f"""
        ANALYZE SKIN ANALYSIS RESULTS AND RECOMMEND PRODUCTS

        Based on the provided JSON analysis results and the product catalog, generate a list of **exactly 20 recommended skincare products**.

        Analysis Results:
        {json.dumps(analysis_results, ensure_ascii=False, indent=4)}

        Product Catalog:
        {json.dumps(self.product_catalog, ensure_ascii=False, indent=4)}

        Recommendations:
        Analyze the skin conditions (e.g., acne, dark circles, wrinkles) and recommend exactly 20 products that address those concerns while considering the user's skin type and tone. If the information is unavailable, prioritize products suitable for all skin types and tones. Ensure that the recommendations are diverse and include a variety of product types (e.g., cleansers, moisturizers, serums). Each recommendation must include the title, price, and image.
        """
        result = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "price": {"type": "number"},
                            "picture": {"type": "string"}
                        },
                        "required": ["title", "price", "picture"]
                    }
                },
            ),
        )

        # Parse the response
        recommendations = json.loads(result.text)

        # Search for products based on the recommendations
        full_recommendations = [
            self._search_product_by_title(rec["title"]) for rec in recommendations
            if self._search_product_by_title(rec["title"]) is not None
        ]

        return full_recommendations
