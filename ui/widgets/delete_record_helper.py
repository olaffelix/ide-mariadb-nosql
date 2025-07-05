from PyQt5.QtWidgets import QMessageBox

class DeleteRecordHelper:
    @staticmethod
    def confirm_and_delete(parent, table_widget, filtered_data, columns, conn, db, table, load_table_data):
        row = table_widget.currentRow()
        if row < 0 or row >= len(filtered_data):
            QMessageBox.warning(parent, 'Eliminar Registro', 'Selecciona un registro para eliminar.')
            return
        pk = filtered_data[row]['_pk']
        if pk is None:
            QMessageBox.warning(parent, 'Eliminar Registro', 'No se puede eliminar: no se encontró la llave primaria.')
            return
        reply = QMessageBox.question(parent, 'Eliminar Registro', '¿Estás seguro de eliminar este registro?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                import pymysql
                connection = pymysql.connect(
                    host=conn['host'], user=conn['user'], password=conn['password'], port=conn['port'], database=db
                )
                with connection.cursor() as cursor:
                    pk_col = columns[0]
                    cursor.execute(f"DELETE FROM `{table}` WHERE `{pk_col}`=%s", (pk,))
                    connection.commit()
                connection.close()
                load_table_data()
                QMessageBox.information(parent, 'Éxito', 'Registro eliminado correctamente.')
            except Exception as e:
                QMessageBox.critical(parent, 'Error', f'Error al eliminar registro: {e}')
