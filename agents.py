# Импорт необходимых модулей
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum

# Настройка логирования
logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Типы агентов в системе"""
    ADMISSION = "admission"  # Поступление
    SCHOLARSHIP = "scholarship"  # Стипендии
    ACADEMIC = "academic"  # Учебные вопросы
    STUDENT_LIFE = "student_life"  # Студенческая жизнь
    GENERAL = "general"  # Общие вопросы


class BaseAgent(ABC):
    """
    Базовый класс для всех агентов системы.
    
    Каждый агент должен наследоваться от этого класса и реализовывать
    метод process_message для обработки сообщений пользователей.
    """
    
    def __init__(self, agent_type: AgentType, name: str, description: str):
        self.agent_type = agent_type
        self.name = name
        self.description = description
        
    @abstractmethod
    def can_handle(self, message: str, language: str = "ru") -> float:
        """
        Определяет, может ли агент обработать данное сообщение.
        
        Args:
            message: Сообщение пользователя
            language: Язык сообщения
            
        Returns:
            float: Уверенность от 0.0 до 1.0 в том, что агент может обработать сообщение
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self, language: str = "ru") -> str:
        """
        Возвращает системный промпт для данного агента.
        
        Args:
            language: Язык для промпта
            
        Returns:
            str: Системный промпт
        """
        pass
    
    def get_keywords(self, language: str = "ru") -> List[str]:
        """
        Возвращает ключевые слова для определения релевантности агента.
        
        Args:
            language: Язык ключевых слов
            
        Returns:
            List[str]: Список ключевых слов
        """
        return []
    
    def process_message(self, message: str, language: str = "ru") -> Dict[str, Any]:
        """
        Обрабатывает сообщение пользователя.
        
        Args:
            message: Сообщение пользователя
            language: Язык сообщения
            
        Returns:
            Dict: Результат обработки с ключами 'response', 'confidence', 'context_used'
        """
        try:
            # Import here to avoid circular imports
            from mistral_client import MistralClient
            
            # Initialize Mistral client
            mistral_client = MistralClient()
            
            # Try to get relevant context, but handle import errors gracefully
            context = ""
            context_used = False
            try:
                from utils import get_relevant_context
                context = get_relevant_context(message, language)
                context_used = bool(context.strip())
            except ImportError:
                logger.warning("Unable to import context retrieval, using empty context")
            
            # Получаем ответ от Mistral
            response = mistral_client.get_response(message, context, language)
            
            return {
                'response': response,
                'confidence': self.can_handle(message, language),
                'context_used': context_used,
                'agent_type': self.agent_type.value,
                'agent_name': self.name
            }
            
        except Exception as e:
            logger.error(f"Error in {self.name} agent: {str(e)}")
            fallback = self._get_fallback_response(language)
            return {
                'response': fallback,
                'confidence': 0.1,
                'context_used': False,
                'agent_type': self.agent_type.value,
                'agent_name': self.name
            }
    
    def _get_fallback_response(self, language: str = "ru") -> str:
        """Возвращает резервный ответ при ошибке"""
        fallback_responses = {
            'ru': f"Извините, у меня возникла ошибка при обработке вашего запроса по теме '{self.description}'. Пожалуйста, обратитесь в приемную комиссию.",
            'kz': f"Кешіріңіз, '{self.description}' тақырыбы бойынша сұрауыңызды өңдеу кезінде қате орын алды. Қабылдау комиссиясына хабарласыңыз."
        }
        return fallback_responses.get(language, fallback_responses['ru'])


class AdmissionAgent(BaseAgent):
    """Агент для обработки вопросов поступления"""
    
    def __init__(self):
        super().__init__(
            AgentType.ADMISSION,
            "Агент поступления",
            "Вопросы поступления и зачисления"
        )
    
    def can_handle(self, message: str, language: str = "ru") -> float:
        """Определяет релевантность для вопросов поступления"""
        keywords = self.get_keywords(language)
        message_lower = message.lower()
        
        # Подсчитываем количество ключевых слов в сообщении
        keyword_count = sum(1 for keyword in keywords if keyword in message_lower)
        
        # Базовая уверенность на основе ключевых слов
        confidence = min(keyword_count * 0.3, 0.9)
        
        # Дополнительные проверки
        if any(word in message_lower for word in ['поступ', 'зачисл', 'абитур', 'прием']):
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def get_keywords(self, language: str = "ru") -> List[str]:
        """Ключевые слова для поступления"""
        if language == "kz":
            return [
                "қабылдау", "түсу", "өтініш", "құжат", "емтихан",
                "балл", "грант", "ақылы", "мамандық", "факультет"
            ]
        return [
            "поступление", "поступить", "зачисление", "документы", "экзамен",
            "балл", "грант", "платное", "специальность", "факультет",
            "абитуриент", "прием", "заявление", "вступительный"
        ]
    
    def get_system_prompt(self, language: str = "ru") -> str:
        """Системный промпт для агента поступления"""
        if language == "kz":
            return """Сіз Қызылорда "Болашақ" университетінің қабылдау жөніндегі мамансыз. 
            Абитуриенттерге қабылдау, құжаттар, емтихандар, мамандықтар және 
            грант орындары туралы сұрақтарға жауап беріңіз. 
            Нақты және пайдалы ақпарат беріңіз."""
        
        return """Вы - специалист по поступлению в Кызылординский университет "Болашак". 
        Отвечайте на вопросы абитуриентов о поступлении, документах, экзаменах, 
        специальностях и грантовых местах. 
        Предоставляйте точную и полезную информацию."""


class ScholarshipAgent(BaseAgent):
    """Агент для обработки вопросов о стипендиях"""
    
    def __init__(self):
        super().__init__(
            AgentType.SCHOLARSHIP,
            "Агент стипендий",
            "Вопросы стипендий и финансовой поддержки"
        )
    
    def can_handle(self, message: str, language: str = "ru") -> float:
        """Определяет релевантность для вопросов стипендий"""
        keywords = self.get_keywords(language)
        message_lower = message.lower()
        
        keyword_count = sum(1 for keyword in keywords if keyword in message_lower)
        confidence = min(keyword_count * 0.35, 0.9)
        
        # Дополнительные проверки для финансовых вопросов
        if any(word in message_lower for word in ['стипенд', 'деньги', 'оплат', 'финанс']):
            confidence += 0.25
        
        return min(confidence, 1.0)
    
    def get_keywords(self, language: str = "ru") -> List[str]:
        """Ключевые слова для стипендий"""
        if language == "kz":
            return [
                "шәкіақы", "жәрдемақы", "қаржы", "ақша", "төлем",
                "көмек", "грант", "несие", "жеңілдік"
            ]
        return [
            "стипендия", "стипендии", "деньги", "оплата", "финансы",
            "помощь", "поддержка", "грант", "кредит", "льгота"
        ]
    
    def get_system_prompt(self, language: str = "ru") -> str:
        """Системный промпт для агента стипендий"""
        if language == "kz":
            return """Сіз "Болашақ" университетінің шәкіақы және қаржылық көмек жөніндегі маманыз.
            Студенттерге шәкіақылар, жәрдемақылар, қаржылық көмек және төлем мәселелері 
            туралы сұрақтарға жауап беріңіз."""
        
        return """Вы - специалист по стипендиям и финансовой поддержке университета "Болашак".
        Отвечайте на вопросы студентов о стипендиях, пособиях, финансовой помощи 
        и вопросах оплаты обучения."""


class AcademicAgent(BaseAgent):
    """Агент для обработки учебных вопросов"""
    
    def __init__(self):
        super().__init__(
            AgentType.ACADEMIC,
            "Академический агент",
            "Учебные вопросы и образовательный процесс"
        )
    
    def can_handle(self, message: str, language: str = "ru") -> float:
        """Определяет релевантность для учебных вопросов"""
        keywords = self.get_keywords(language)
        message_lower = message.lower()
        
        keyword_count = sum(1 for keyword in keywords if keyword in message_lower)
        confidence = min(keyword_count * 0.3, 0.9)
        
        # Проверка на учебные темы
        if any(word in message_lower for word in ['учеб', 'занят', 'предмет', 'курс', 'экзамен']):
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def get_keywords(self, language: str = "ru") -> List[str]:
        """Ключевые слова для учебных вопросов"""
        if language == "kz":
            return [
                "сабақ", "пән", "оқу", "емтихан", "зачет", "курс",
                "кесте", "дәрісхана", "оқытушы", "балл", "академия"
            ]
        return [
            "занятие", "предмет", "учеба", "экзамен", "зачет", "курс",
            "расписание", "аудитория", "преподаватель", "оценка", "академический"
        ]
    
    def get_system_prompt(self, language: str = "ru") -> str:
        """Системный промпт для академического агента"""
        if language == "kz":
            return """Сіз "Болашақ" университетінің оқу үдерісі жөніндегі маманыз.
            Студенттерге сабақтар, пәндер, емтихандар, кестелер және оқу үдерісі 
            туралы сұрақтарға жауап беріңіз."""
        
        return """Вы - специалист по учебному процессу университета "Болашак".
        Отвечайте на вопросы студентов о занятиях, предметах, экзаменах, 
        расписании и образовательном процессе."""


class StudentLifeAgent(BaseAgent):
    """Агент для обработки вопросов студенческой жизни"""
    
    def __init__(self):
        super().__init__(
            AgentType.STUDENT_LIFE,
            "Агент студенческой жизни",
            "Студенческая жизнь и внеучебная деятельность"
        )
    
    def can_handle(self, message: str, language: str = "ru") -> float:
        """Определяет релевантность для вопросов студенческой жизни"""
        keywords = self.get_keywords(language)
        message_lower = message.lower()
        
        keyword_count = sum(1 for keyword in keywords if keyword in message_lower)
        confidence = min(keyword_count * 0.35, 0.9)
        
        # Проверка на темы студенческой жизни
        if any(word in message_lower for word in ['общежит', 'кружок', 'спорт', 'мероприят']):
            confidence += 0.25
        
        return min(confidence, 1.0)
    
    def get_keywords(self, language: str = "ru") -> List[str]:
        """Ключевые слова для студенческой жизни"""
        if language == "kz":
            return [
                "жатақхана", "спорт", "шара", "үйірме", "клуб",
                "фестиваль", "демалыс", "досуг", "белсенділік"
            ]
        return [
            "общежитие", "спорт", "мероприятие", "кружок", "клуб",
            "фестиваль", "отдых", "досуг", "активность", "внеучебный"
        ]
    
    def get_system_prompt(self, language: str = "ru") -> str:
        """Системный промпт для агента студенческой жизни"""
        if language == "kz":
            return """Сіз "Болашақ" университетінің студенттік өмір жөніндегі маманыз.
            Студенттерге жатақхана, спорт, шаралар, үйірмелер және оқудан тыс 
            қызмет туралы сұрақтарға жауап беріңіз."""
        
        return """Вы - специалист по студенческой жизни университета "Болашак".
        Отвечайте на вопросы о общежитии, спорте, мероприятиях, кружках 
        и внеучебной деятельности."""


class GeneralAgent(BaseAgent):
    """Агент для обработки общих вопросов"""
    
    def __init__(self):
        super().__init__(
            AgentType.GENERAL,
            "Общий агент",
            "Общие вопросы и информация об университете"
        )
    
    def can_handle(self, message: str, language: str = "ru") -> float:
        """Всегда готов обработать любой вопрос с низкой уверенностью"""
        # Общий агент всегда может ответить, но с низкой уверенностью
        # Если никто другой не может ответить, он станет резервным
        return 0.3
    
    def get_keywords(self, language: str = "ru") -> List[str]:
        """Общие ключевые слова"""
        if language == "kz":
            return [
                "университет", "болашақ", "ақпарат", "сұрақ", "көмек",
                "орналасу", "байланыс", "сайт"
            ]
        return [
            "университет", "болашак", "информация", "вопрос", "помощь",
            "адрес", "контакт", "сайт"
        ]
    
    def get_system_prompt(self, language: str = "ru") -> str:
        """Системный промпт для общего агента"""
        if language == "kz":
            return """Сіз Қызылорда "Болашақ" университетінің жалпы ақпарат беруші маманыз.
            Университет туралы жалпы сұрақтарға жауап беріңіз және қажет болса 
            студенттерді тиісті мамандарға бағыттаңыз."""
        
        return """Вы - общий помощник Кызылординского университета "Болашак".
        Отвечайте на общие вопросы об университете и при необходимости 
        направляйте студентов к соответствующим специалистам."""


class AgentRouter:
    """
    Маршрутизатор агентов.
    
    Определяет наиболее подходящего агента для обработки сообщения пользователя
    на основе анализа содержания и уверенности каждого агента.
    """
    
    def __init__(self):
        # Инициализируем всех агентов
        self.agents = [
            AdmissionAgent(),
            ScholarshipAgent(),
            AcademicAgent(),
            StudentLifeAgent(),
            GeneralAgent()
        ]
        
        logger.info(f"AgentRouter initialized with {len(self.agents)} agents")
    
    def route_message(self, message: str, language: str = "ru") -> Dict[str, Any]:
        """
        Маршрутизирует сообщение к наиболее подходящему агенту.
        
        Args:
            message: Сообщение пользователя
            language: Язык сообщения
            
        Returns:
            Dict: Результат обработки сообщения выбранным агентом
        """
        try:
            # Получаем уверенность каждого агента
            agent_confidences = []
            for agent in self.agents:
                confidence = agent.can_handle(message, language)
                agent_confidences.append((agent, confidence))
                logger.debug(f"Agent {agent.name}: confidence {confidence:.2f}")
            
            # Сортируем по уверенности (по убыванию)
            agent_confidences.sort(key=lambda x: x[1], reverse=True)
            
            # Выбираем агента с наибольшей уверенностью
            best_agent, best_confidence = agent_confidences[0]
            
            logger.info(f"Selected agent: {best_agent.name} (confidence: {best_confidence:.2f})")
            
            # Обрабатываем сообщение выбранным агентом
            result = best_agent.process_message(message, language)
            result['selected_confidence'] = best_confidence
            
            return result
            
        except Exception as e:
            logger.error(f"Error in agent routing: {str(e)}")
            # В случае ошибки используем общего агента
            general_agent = GeneralAgent()
            result = general_agent.process_message(message, language)
            result['selected_confidence'] = 0.1
            result['error'] = str(e)
            return result
    
    def get_available_agents(self) -> List[Dict[str, str]]:
        """
        Возвращает список доступных агентов.
        
        Returns:
            List[Dict]: Список агентов с их описанием
        """
        return [
            {
                'type': agent.agent_type.value,
                'name': agent.name,
                'description': agent.description
            }
            for agent in self.agents
        ]