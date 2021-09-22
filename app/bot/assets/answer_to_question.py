import logging
import os
import pymorphy2
from app.models import FaqList
from google.cloud import language_v1


logger = logging.getLogger('main_logger')


def get_words_with_normal_form(words_and_weights):
    """
    Приводит каждое слово к нормальной форме
    return words_and_weights = List[tuple(str, int)]
    """
    morph = pymorphy2.MorphAnalyzer()
    temp_list = []
    for word_and_weight in words_and_weights:
        temp_list.append((morph.parse(word_and_weight[0])[0].normal_form, 1.0))
    words_and_weights = temp_list
    return words_and_weights


# def get_answer_pymorphy(words_in_normal_form, faqs):
#     rank = dict()
#     logger.debug(words_in_normal_form)
#     for n, faq in enumerate(faqs):
#         if faq.answer:
#             raiting = 0
#             for word in words_in_normal_form:
#                 if word in faq.keywords:
#                     raiting += 1
#             if raiting:
#                 rank[faq.id] = raiting
#     # сортируем словарь по наивысшему РАНГУ
#     rank = [(k, rank[k]) for k in sorted(rank, key=rank.get, reverse=True)]
#     logger.debug(rank)
#     id = rank[0][0]
#     faq = FaqList.objects.filter(id=id)[0]
#     logger.debug(faq.answer)


def get_google_analyzing_syntax(text_content):
    """
    С помощью Google Analyzing Syntax формирует спсисок тегов с весами.
    return words_and_weights = List[tuple(str, int)]
    """
    logger.debug("определяем слова и присваеваем веса из "
                 "пользовательского запроса (1.0)")
    credential_path = "/home/debian/webapps/app-nissanbotpyt/" \
                      "nissanbotai-d7825e28da16.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    client = language_v1.LanguageServiceClient()
    type_ = language_v1.Document.Type.PLAIN_TEXT
    language = "ru"
    document = {"content": text_content, "type_": type_, "language": language}
    encoding_type = language_v1.EncodingType.UTF8
    logger.debug(f"выполняем запрос к Google API ({text_content})")
    response = client.analyze_syntax(
        request={'document': document, 'encoding_type': encoding_type}
    )
    words_and_weights = list()
    logger.debug("формируем токены пользовательского запроса с весами")
    logger.debug("\tTokens from Google:")
    # предлог, союз, числительное, местоимение, частица, пунктуация, наречие,
    # определитель, остальное
    stop_part_of_speech = ['ADP', 'CONJ', 'NUM', 'PRON', 'PRT', 'PUNCT',
                           'ADV', 'DET', 'X']
    for token in response.tokens:
        part_of_speech = language_v1.PartOfSpeech.Tag(
            token.part_of_speech.tag
        ).name
        if part_of_speech in stop_part_of_speech:
            continue
        word = token.text.content
        weight = 1.0
        logger.debug(f"\tname: {word}\tsalience: {weight}\t"
                     f"part_of_speach: {part_of_speech}")
        words_and_weights.append((word, weight))
    logger.debug(f"words_and_weights: {words_and_weights}")
    words_and_weights = get_words_with_normal_form(words_and_weights)
    logger.debug(f"words_and_weights with normal form: {words_and_weights}")
    return words_and_weights


# def get_google_analyzing_entities(text_content):
#     """
#     Функция формирует сущности пользовательского запроса с весами
#     return words_and_weights = list[tuple(str, int)]
#     """
#     # определяем слова и их веса из пользовательского запроса
#     logger.debug("определяем слова и их веса из пользовательского запроса")
#     credential_path = "/home/debian/webapps/app-nissanbotpyt/" \
#                       "nissanbotai-d7825e28da16.json"
#     os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
#     client = language_v1.LanguageServiceClient()
#     type_ = language_v1.Document.Type.PLAIN_TEXT
#     document = {"content": text_content, "type_": type_, "language": "ru"}
#     encoding_type = language_v1.EncodingType.UTF8
#     logger.debug("выполняем запрос к Google API")
#     response = client.analyze_entities(
#         request={'document': document, 'encoding_type': encoding_type}
#     )
#     words_and_weights = list()
#     logger.debug("формируем сущности пользовательского запроса с весами")
#     logger.debug("\tEntities from Google:")
#     for entity in response.entities:
#         word = entity.name
#         weight = entity.salience
#         logger.debug(f"\tname: {word}\tsalience: {weight}")
#         words_and_weights.append((word, weight))
#     return words_and_weights


def get_rank(faqs, words_and_weights):
    """
    Функция формирует словарь "faq.id"->"общий вес" на основании google analyze
    return rank = dict({int: int})
    """
    logger.debug("формирует словарь с ранжированием по значению "
                 "'faq.id' -> 'общий вес' на основании google analyze")
    rank = dict()
    # цикл по записям
    for faq in faqs:
        score = 0
        # циклом берём слово, проверяем его вхождение в поле ключевые слова,
        # если есть, то вес этого слова плюсуем к общему весу этой записи
        for word_and_weight in words_and_weights:
            word = word_and_weight[0]
            weight = word_and_weight[1]
            if word in faq.keywords:
                score += weight
        # добавляем в словарь "id записи" -> "общий вес"
        if score:
            rank[faq.id] = score
    return rank


def save_question(text_content, words_and_weights):
    """
    Функция сохраняет заданный пользователем вопрос с ключевыми словами, 
    если на него не бы найден ответ
    """
    exist_question = FaqList.objects.filter(question=text_content)
    if exist_question:
        logger.debug(f"exist_question: {exist_question}")
        logger.debug(f"Вопрос '{text_content}' уже существует, не записываем.")
        return
    keywords = ", ".join(
        [word_and_weight[0] for word_and_weight in words_and_weights]
    )
    logger.debug(f"question: {text_content}")
    logger.debug(f"keywords: {keywords}")
    faq = FaqList(question=text_content, keywords=keywords)
    faq.save()


def get_answer(text_content):
    """
    Функция возвращает ответ на запрос пользователя
    return faq = FaqList()
    """
    # выбираем все записи с ответами, фильтруем по совпадению
    # с пользовательским вопросом, отдаём ответ
    logger.debug("Ищем совпадение с вопросом по записям")
    faq = FaqList.objects.exclude(answer__exact='').filter(
        question__exact=text_content)
    if faq.count():
        logger.debug("Такой же вопрос найден в записях, возвращаем FaqList")
        return faq[0]
    logger.debug("Вопрос в записях не найден.")

    # ищем по ключевым словам, используя все слова и их веса от гугл,
    # предварительно отобрав все записи с ключевыми словами
    logger.debug("ищем по ключевым словам")
    faqs = FaqList.objects.exclude(answer__exact='').exclude(keywords__exact='')
    if not faqs:
        logger.debug("Отсутствуют записи с ответами и с ключевыми словами, "
                     "сохраняем")
        return None
    words_and_weights = get_google_analyzing_syntax(text_content)
    # words_and_weights = get_google_analyzing_entities(text_content)
    rank = get_rank(faqs, words_and_weights)
    if not rank:
        # если поиск по ключевым словам не дал результатов, то создаем 
        # запись с вопросом пользователя, в поле Ключевые слова - 
        # слова с весами от гугл, поля Ответ, Ссылка - пустые
        logger.debug("поиск по ключевым словам не дал результатов, "
                     "создаем запись")
        save_question(text_content, words_and_weights)
        return None
    # сортируем словарь по убыванию значений (общий вес),
    # получаем list[tuple(faq.id, score), ...]
    rank = [(k, rank[k]) for k in sorted(rank, key=rank.get, reverse=True)]
    logger.debug(f"rank dict: {rank}")
    faq_id = rank[0][0]
    # достаём нужную запись
    faq = FaqList.objects.filter(id=faq_id)[0]
    logger.debug("отдаём FaqList()")
    return faq
