from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/todolist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Task(db.Model):
    __tablename__ = 'tarefas'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(50), nullable=False)


@app.route('/tarefas', methods=['GET'])
def obter_tarefas():
    tarefas = Task.query.all()
    return jsonify([{'id': tarefa.id, 'titulo': tarefa.titulo, 'estado': tarefa.estado} for tarefa in tarefas])


@app.route('/tarefas/<int:id>', methods=['GET'])
def obter_tarefa_por_id(id):
    tarefa = Task.query.get(id)
    if tarefa:
        return jsonify({'id': tarefa.id, 'titulo': tarefa.titulo, 'estado': tarefa.estado})
    else:
        abort(404, description="Tarefa não encontrada")


@app.route('/tarefas/<int:id>', methods=['PUT'])
def editar_tarefa_por_id(id):
    tarefa_existente = Task.query.get(id)

    if tarefa_existente:
        dados_alterados = request.get_json()
        tarefa_existente.titulo = dados_alterados['titulo']
        tarefa_existente.estado = dados_alterados['estado']
        db.session.commit()
        return jsonify({'id': tarefa_existente.id, 'titulo': tarefa_existente.titulo, 'estado': tarefa_existente.estado})
    else:
        abort(404, description="Tarefa não encontrada")


def validar_tarefa(dados):
    if 'titulo' not in dados or 'estado' not in dados:
        abort(400, description="Campos 'titulo' e 'estado' são obrigatórios.")
    if not isinstance(dados['titulo'], str) or not isinstance(dados['estado'], str):
        abort(400, description="Campos 'titulo' e 'estado' devem ser strings.")
        

@app.route('/tarefas', methods=['POST'])
def incluir_nova_tarefa():
    nova_tarefa = request.get_json()
    validar_tarefa(nova_tarefa)
    
    nova_tarefa_model = Task(titulo=nova_tarefa['titulo'], estado=nova_tarefa['estado'])
    db.session.add(nova_tarefa_model)
    db.session.commit()
    
    return jsonify({'id': nova_tarefa_model.id, 'titulo': nova_tarefa_model.titulo, 'estado': nova_tarefa_model.estado})


@app.route('/tarefas/<int:id>', methods=['DELETE'])
def excluir_tarefa_por_id(id):
    tarefa_existente = Task.query.get(id)
    if tarefa_existente:
        db.session.delete(tarefa_existente)
        db.session.commit()
        return jsonify({'mensagem': 'Tarefa excluída com sucesso'})
    else:
        abort(404, description="Tarefa não encontrada")


if __name__ == '__main__':
    db.create_all()
    app.run(port=5000, host='localhost', debug=True)