def get_category_ids(cursor):
    cat_dict = {}
    cursor.execute("select * from plant_category")
    
    cats = cursor.fetchall()
    for data in cats:
        cat_dict[data[1]] = data[0]

    return cat_dict
