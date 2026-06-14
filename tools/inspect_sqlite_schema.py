import sqlite3


def main():
    con = sqlite3.connect(r"ExamOnline\db.sqlite3")
    cur = con.cursor()
    tables = [
        row[0]
        for row in cur.execute(
            "select name from sqlite_master "
            "where type='table' and name not like 'sqlite_%' "
            "order by name"
        )
    ]
    for table in tables:
        print(f"TABLE {table}")
        for column in cur.execute(f"pragma table_info({table})"):
            cid, name, col_type, notnull, default, pk = column
            print(f"  COL {name} {col_type} notnull={notnull} default={default} pk={pk}")
        foreign_keys = list(cur.execute(f"pragma foreign_key_list({table})"))
        for fk in foreign_keys:
            print(f"  FK {fk}")
        indexes = list(cur.execute(f"pragma index_list({table})"))
        for idx in indexes:
            print(f"  IDX {idx}")


if __name__ == "__main__":
    main()
