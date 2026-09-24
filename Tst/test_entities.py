from Src.Core.abstract_entity import abstract_model
from Src.Core.exception import arguments_exception
import pytest

#TODO Написать анотации, исправить проверки, переписать исключение, переписать codebase

#Тест абстрактной сущности
class test_entity(abstract_model):
  pass

def test_abstract_model_get_id_notNull():
  """
  Тест для проверки создания правильно id
  """
  entity = test_entity()
  result = entity.id
  #Проверка
  assert result != " "
  assert result is not None

def test_abstract_model_get_diff_id():
  """
  Тест для проверки создания разных идентификатороф
  """
  entity1 = test_entity()
  entity2 = test_entity()
  code1 = entity1.id
  code2 = entity2.id
  assert code1 != code2
  assert code1 != " "
  assert code2 != " "

def test_abstract_model_entitites_have_same_code():
  """
  Тест для проверка на сравнение двух сущностей
  """
  entity1 = test_entity()
  entity2 = test_entity()
  entity1.id = "fff"
  entity2.id = "fff"
  code1 = entity1.id
  code2 = entity2.id
  assert code1 == code2

def test_abstract_model_catch_name_error():
  """
  Тест для ловки ошибки неправильного имени
  """
  entity = test_entity()
  with pytest.raises(arguments_exception):
    entity.name = ""
  assert True  


