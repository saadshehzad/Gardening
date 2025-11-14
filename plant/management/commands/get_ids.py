def get_category_ids(cursor):
    cat_dict = {}
    cursor.execute("select * from plant_category")
    
    cats = cursor.fetchall()
    for data in cats:
        cat_dict[data[1]] = data[0]

    return cat_dict


def get_llm_ids(cursor):
    cursor.execute("SELECT id, name FROM plant_llm")
    return {row[1]: row[0] for row in cursor.fetchall()}
