from Connection.connection import connect,connection_select

def getModelAll():
    dataBase = connect()
    if not (isinstance(dataBase, list)):
        cursorObject = dataBase.cursor()
        try:
            stmt = ("SELECT "
                        "a.idModel,a.title,a.nameLabelX,a.nameLabelY,a.position,a.nameNivel,b.nameColor "
                    "FROM "
                        "model a,color b "
                    "WHERE a.idColor=b.idColor "
                    "ORDER BY a.position ASC")
            myresult = connection_select(cursorObject,stmt)
            cursorObject.close()
            dataBase.close()
            return myresult
        except Exception as e:
            error_msg = str(e)
            cursorObject.close()
            dataBase.close()
            return [{'message': f'Error en consulta getModelAll: {error_msg}'}]
    else:
        error_message = dataBase[0]['message']
        return [{'message':error_message}]
        