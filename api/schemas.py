from marshmallow import Schema, fields


class Email(Schema):
    email = fields.Email()

class IdEmail(Email):
    id = fields.Str()

class EmailPass(Email):
    password = fields.Str()
