from marshmallow import Schema, fields


class Email(Schema):
    email = fields.Email()

class UserId(Schema):
    id = fields.Str()

class Interlocutor(UserId):
    pass

class IdEmail(UserId, Email):
    pass

class EmailPass(Email):
    password = fields.Str()


class ConvSchema(Schema):
    id = fields.Str()
    created_at = fields.Int(required=True)
    users = fields.List(fields.Str(),
                        required=True)


class ChatMessage(Schema):
    id = fields.Str(required=True)
    author = fields.Str(required=True)
    conversation = fields.Str(required=True)
    timestamp = fields.Str(required=True)
    content = fields.Str(required=True)
    read = fields.Bool(required=False)
