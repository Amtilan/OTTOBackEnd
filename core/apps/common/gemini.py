from dataclasses import dataclass, field
import os
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
    # Параметры с значениями по умолчанию
    catalog_file: str = field(default=os.path.join(os.path.dirname(__file__), 'combined.json'), init=False)
    api_key: str = env('GOOGLE_API_KEY')
    model_name: str = env('MODEL_NAME')
    face_path: Optional[str] = None
    pred_results: BasePredResults = field(default_factory=ORMPredResults)

    # Поля, инициализируемые внутренне
    product_catalog: List[dict] = field(init=False, default_factory=list)
    recommendations: Optional[List[dict]] = field(init=False, default=None)
    analysis_results: dict = field(init=False, default_factory=dict)
    model: genai.GenerativeModel = field(init=False)

    def __post_init__(self):
        self._validate_required_fields()
        self._configure_gemini()
        self._load_data()
        self.analysis_results = self._get_analysis_results()
        self.recommendations = self._generate_recommendations()

    def _validate_required_fields(self):
        if not self.face_path:
            raise ValueError("face_path is required")
        if not self.api_key:
            raise EnvironmentError("GOOGLE_API_KEY is not set in environment variables")

    # Остальные методы остаются без изменений
    def _configure_gemini(self) -> None:
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    @staticmethod
    def _load_json(file_path: str) -> list:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)  # Ожидается, что результат будет списком словарей
    
    def _load_data(self) -> None:
        self.product_catalog = self._load_json(self.catalog_file)
        
    def _search_product_by_title(self, title: str) -> Optional[dict]:
        for product in self.product_catalog:
            print(type(product))
            if product.get("title") == title:
                return product
        return None

    def _get_analysis_results(self) -> dict:
        return self.pred_results.get_better_pred_results(image_file_path=self.face_path) or {}


    def _generate_recommendations(self) -> List[dict]:
        analysis_report = self._generate_analysis_report()  # Generate the report

        prompt = f"""
        СГЕНЕРИРУЙ СПИСОК ИЗ 20 РЕКОМЕНДУЕМЫХ ПРОДУКТОВ

        Основываясь на предоставленном отчете о состоянии кожи и каталоге продуктов, сгенерируй список из ровно 20 рекомендуемых продуктов по уходу за кожей.

        Отчет о состоянии кожи:
        {analysis_report}

        Каталог продуктов:
        {json.dumps(self.product_catalog, ensure_ascii=False, indent=4)}

        Рекомендации:
        Проанализируй состояние кожи (например, акне, темные круги, морщины) и порекомендуй ровно 20 продуктов, которые решают эти проблемы, учитывая тип кожи пользователя. Если информация недоступна, отдавай предпочтение продуктам, подходящим для всех типов кожи. Убедись, что рекомендации разнообразны и включают различные типы продуктов (например, очищающие средства, увлажняющие кремы, сыворотки). Каждая рекомендация должна включать название, цену и изображение.
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

        recommendations = json.loads(result.text)
        full_recommendations = [
            self._search_product_by_title(rec["title"]) for rec in recommendations
            if self._search_product_by_title(rec["title"]) is not None
        ]

        return full_recommendations


    def _generate_analysis_report(self) -> str:
        """Генерирует отчет о состоянии кожи на основе анализа."""

        results = self.analysis_results
        if not results or 'skin_status' not in results:
            return "Не удалось получить данные для анализа кожи."

        skin_status = results['skin_status']

        report = "📌 Отчет о состоянии кожи**\n\n"

        # 1. Акне и зоны воспаления/пигментации
        report += "1️⃣ **Акне и зоны воспаления/пигментации**\n\n"
        report += "**Проблемы:**\n\n"
        if skin_status.get('acne'):
            acne_confidence = skin_status['acne']['confidence']
            report += f"- Акне (Acne): {'Выраженная проблема' if acne_confidence > 0.7 else 'Присутствует' if acne_confidence > 0.3 else 'Незначительная проблема'}. (Вероятность: {acne_confidence:.6}).\n"
        if skin_status.get('skin_spot'):
            spot_confidence = skin_status['skin_spot']['confidence']
            report += f"- Пятна на коже (Skin Spot): {'Заметная проблема' if spot_confidence > 0.7 else 'Присутствуют' if spot_confidence > 0.3 else 'Незначительные'}. (Вероятность: {spot_confidence:.6}).\n"
        if skin_status.get('mole'):
             mole_confidence = skin_status['mole']['confidence']
             report += f"- Родинки/бородавки (Mole): Присутствуют. (Вероятность: {mole_confidence:6}).\n"


        report += "\n**Положительные моменты:**\n\n"
        if skin_status.get('blackhead'):
            blackhead_confidence = skin_status['blackhead']['confidence']
            report += f"- Черные точки (Blackhead): {'Практически отсутствуют' if blackhead_confidence < 0.1 else 'Присутствуют в небольшом количестве' if blackhead_confidence < 0.5 else 'Присутствуют'}. (Вероятность: {blackhead_confidence:.6}).\n"

        # 2. Тёмные круги и морщины
        report += "\n2️⃣ **Тёмные круги и морщины**\n\n"
        report += "**Проблемы:**\n\n"
        if skin_status.get('nasolabial_fold'):
            nasolabial_confidence = skin_status['nasolabial_fold']['confidence']
            report += f"- Носогубные складки (Nasolabial Fold): {'Присутствуют' if nasolabial_confidence > 0.5 else 'Слабо выражены'}. (Вероятность: {nasolabial_confidence:.6}).\n"

        report += "\n**Положительные моменты:**\n\n"
        if skin_status.get('dark_circle'):
            dark_circle_confidence = skin_status['dark_circle']['confidence']
            report += f"- Темные круги (Dark Circle): {'Отсутствуют' if dark_circle_confidence > 0.7 else 'Практически отсутствуют'}. (Вероятность: {dark_circle_confidence:.6}).\n"
        if skin_status.get('eye_pouch'):
            eye_pouch_confidence = skin_status['eye_pouch']['confidence']
            report += f"- Мешки под глазами (Eye Pouch): Отсутствуют. (Вероятность: {eye_pouch_confidence:.6}).\n"
        if skin_status.get('forehead_wrinkle'):
            forehead_wrinkle_confidence = skin_status['forehead_wrinkle']['confidence']
            report += f"- Морщины на лбу (Forehead Wrinkle): {'Отсутствуют' if forehead_wrinkle_confidence < 0.1 else 'Присутствуют в небольшом количестве'}. (Вероятность: {forehead_wrinkle_confidence:.6}).\n"
        if skin_status.get('eye_finelines'):
             eye_finelines_confidence = skin_status['eye_finelines']['confidence']
             report += f"- Мелкие морщины вокруг глаз (Eye Finelines): {'Отсутствуют' if eye_finelines_confidence < 0.1 else 'Присутствуют'}. (Вероятность: {eye_finelines_confidence:.6}).\n"
        if skin_status.get('crows_feet'):
             crows_feet_confidence = skin_status['crows_feet']['confidence']
             report += f"- \"Гусиные лапки\" (Crows Feet): {'Отсутствуют' if crows_feet_confidence < 0.1 else 'Присутствуют'}. (Вероятность: {crows_feet_confidence:.6}).\n"
        if skin_status.get('glabella_wrinkle'):
            glabella_wrinkle_confidence = skin_status['glabella_wrinkle']['confidence']
            report += f"- Межбровные морщины (Glabella Wrinkle): {'Отсутствуют' if glabella_wrinkle_confidence < 0.1 else 'Присутствуют'}. (Вероятность: {glabella_wrinkle_confidence:.6}).\n"

        #left_eyelids and right_eyelids
        if skin_status.get('left_eyelids') and skin_status.get('right_eyelids'):
            left_eyelids_confidence = skin_status['left_eyelids']['confidence']
            right_eyelids_confidence = skin_status['right_eyelids']['confidence']
            report += f"- Состояние век (Left Eyelids and Right Eyelids): В норме. (Вероятность: {left_eyelids_confidence:.6} и {right_eyelids_confidence:.6} соответственно).\n"

        # 3. Текстура кожи и поры
        report += "\n3️⃣ **Текстура кожи и поры**\n\n"
        report += "**Проблемы:**\n\n"
        if skin_status.get('pores_left_cheek'):
            pores_left_cheek_confidence = skin_status['pores_left_cheek']['confidence']
            report += f"- Поры на левой щеке (Pores Left Cheek): {'Расширены' if pores_left_cheek_confidence > 0.7 else 'Умеренно расширены' if pores_left_cheek_confidence > 0.3 else 'В норме'}. (Вероятность: {pores_left_cheek_confidence:.6}).\n"
        if skin_status.get('pores_right_cheek'):
            pores_right_cheek_confidence = skin_status['pores_right_cheek']['confidence']
            report += f"- Поры на правой щеке (Pores Right Cheek): {'Сильно расширены' if pores_right_cheek_confidence > 0.7 else 'Расширены' if pores_right_cheek_confidence > 0.3 else 'В норме'}. (Вероятность: {pores_right_cheek_confidence:.6}).\n"
        if skin_status.get('pores_forehead'):
            pores_forehead_confidence = skin_status['pores_forehead']['confidence']
            report += f"- Поры на лбу (Pores Forehead): {'Вероятно, расширены' if pores_forehead_confidence > 0.5 else 'В норме'}. (Вероятность: {pores_forehead_confidence:.6}).\n"

        report += "\n**Положительные моменты:**\n\n"
        if skin_status.get('pores_jaw'):
             pores_jaw_confidence = skin_status['pores_jaw']['confidence']
             report += f"- Поры на подбородке (Pores Jaw): {'В норме' if pores_jaw_confidence > 0.7 else 'Незначительно расширены'}. (Вероятность: {pores_jaw_confidence:.6}).\n"

        # 4. Тип кожи
        report += "\n4️⃣ **Тип кожи**\n\n"
        if skin_status.get('skin_type'):
            skin_type_confidence = skin_status['skin_type']
            skin_types = {
                0: "Тип 0 (Очень сухая)",
                1: "Тип 1 (Сухая)",
                2: "Тип 2 (Комбинированная/Нормальная)",
                3: "Тип 3 (Жирная)"
            }
            
            # Find the most likely skin type
            best_type = max(skin_type_confidence, key=skin_type_confidence.get)
            report += f"- Общий тип кожи: {skin_types.get(best_type, 'Неопределенный тип')}. (Вероятность: {skin_type_confidence[best_type]:.6}).\n\n"

            report += "**Детализация по типам:**\n"
            for type_num, type_desc in skin_types.items():
                confidence = skin_type_confidence.get(type_num, 0)
                report += f"- {type_desc}: {confidence:.6}\n"

        # 5. Общий анализ
        report += "\n5️⃣ **Общий анализ**\n\n"
        report += "**Основные проблемы: "
        main_problems = []
        if skin_status.get('acne') and skin_status['acne']['confidence'] > 0.7:
            main_problems.append("Акне")
        if skin_status.get('skin_spot') and skin_status['skin_spot']['confidence'] > 0.7:
            main_problems.append("Пигментация (пятна на коже)")
        if (skin_status.get('pores_left_cheek') and skin_status['pores_left_cheek']['confidence'] > 0.7) or \
           (skin_status.get('pores_right_cheek') and skin_status['pores_right_cheek']['confidence'] > 0.7):
            main_problems.append("Расширенные поры (особенно на щеках)")
        if skin_status.get('nasolabial_fold') and skin_status['nasolabial_fold']['confidence'] > 0.5:
            main_problems.append("Носогубные складки")
        report += ", ".join(main_problems) + ".\n" if main_problems else "Основные проблемы не выявлены.\n"

        report += "Вторичные/потенциальные проблемы: "
        secondary_problems = []
        if skin_status.get('pores_forehead') and skin_status['pores_forehead']['confidence'] > 0.5:
            secondary_problems.append("Возможное расширение пор на лбу")
        report += ", ".join(secondary_problems) + ".\n" if secondary_problems else "Вторичные проблемы не выявлены.\n"

        report += "Положительные аспекты: "
        positive_aspects = []
        if skin_status.get('dark_circle') and skin_status['dark_circle']['confidence'] > 0.7:
            positive_aspects.append("Отсутствие темных кругов")
        if skin_status.get('eye_pouch') and skin_status['eye_pouch']['confidence'] > 0.7:
            positive_aspects.append("Отсутствие мешков под глазами")
        if skin_status.get('blackhead') and skin_status['blackhead']['confidence'] < 0.1:
             positive_aspects.append("Отсутствие черных точек")
        if skin_status.get('pores_jaw') and skin_status['pores_jaw']['confidence'] >0.7:
            positive_aspects.append("Нормальное состояние пор на подбородке")

        low_wrinkle_types = []
        if skin_status.get('forehead_wrinkle') and skin_status['forehead_wrinkle']['confidence'] < 0.1:
            low_wrinkle_types.append("морщин на лбу")
        if skin_status.get('eye_finelines') and skin_status['eye_finelines']['confidence'] < 0.1:
            low_wrinkle_types.append("мелких морщин вокруг глаз")
        if skin_status.get('crows_feet') and skin_status['crows_feet']['confidence'] < 0.1:
            low_wrinkle_types.append("\"гусиных лапок\"")
        if skin_status.get('glabella_wrinkle') and skin_status['glabella_wrinkle']['confidence'] < 0.1:
             low_wrinkle_types.append("межбровных морщин")
        if low_wrinkle_types:
            positive_aspects.append("Отсутствие большинства типов морщин (" + ", ".join(low_wrinkle_types) + ")")
        if skin_status.get('left_eyelids') and skin_status.get('right_eyelids') and skin_status['left_eyelids']['confidence'] > 0.7 and skin_status['right_eyelids']['confidence'] > 0.7:
            positive_aspects.append("Хорошее состояние век")

        report += ", ".join(positive_aspects) + ".\n" if positive_aspects else "Положительные аспекты не выявлены.\n"



        return report