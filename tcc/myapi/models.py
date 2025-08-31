from django.db import models
# from neomodel import StructuredNode, StringProperty, IntegerProperty,UniqueIdProperty, RelationshipTo

# # Create your models here.


# class Pessoa(StructuredNode):
#     code = StringProperty(unique_index=True, required=True)
#     name = StringProperty(index=True, default="city")

# class Organizacao(StructuredNode):
#     uid = UniqueIdProperty()
#     name = StringProperty(unique_index=True)
#     age = IntegerProperty(index=True, default=0)

#     # Relations :
#     city = RelationshipTo(City, 'LIVES_IN')
#     friends = RelationshipTo('Person','FRIEND')