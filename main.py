import sys
import database


def print_table(headers: list[str], rows: list[list]) -> None:
    """Print a clean formatted ascii table."""
    if not rows:
        print("  (Записів не знайдено / Таблиця порожня)")
        return

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            val_str = str(val)
            if len(val_str) > col_widths[i]:
                col_widths[i] = len(val_str)

    header_line = " | ".join(f"{headers[i]:<{col_widths[i]}}" for i in range(len(headers)))
    separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    print(header_line)
    print(separator)
    for row in rows:
        row_line = " | ".join(f"{str(row[i]):<{col_widths[i]}}" for i in range(len(row)))
        print(row_line)


def list_students_ui():
    print("\n--- Список студентів ---")
    students = database.get_all_students()
    headers = ["ID", "ПІБ / Ім'я", "Вік", "Спеціальність"]
    rows = [[s["id"], s["name"], s["age"], s["major"]] for s in students]
    print_table(headers, rows)


def list_courses_ui():
    print("\n--- Список курсів ---")
    courses = database.get_all_courses()
    headers = ["ID Курсу", "Назва курсу", "Викладач"]
    rows = [[c["course_id"], c["course_name"], c["instructor"]] for c in courses]
    print_table(headers, rows)


def add_student_ui():
    print("\n--- Додавання нового студента ---")
    name = input("Введіть ПІБ або ім'я студента: ").strip()
    if not name:
        print("Помилка: Ім'я не може бути порожнім!")
        return

    try:
        age = int(input("Введіть вік студента: ").strip())
        if age <= 0:
            print("Помилка: Вік має бути додатним числом!")
            return
    except ValueError:
        print("Помилка: Некоректний формат віку!")
        return

    major = input("Введіть спеціальність студента: ").strip()
    if not major:
        print("Помилка: Спеціальність не може бути порожньою!")
        return

    student_id = database.add_student(name, age, major)
    print(f"Успішно додано студента! ID: {student_id}")


def add_course_ui():
    print("\n--- Додавання нового курсу ---")
    course_name = input("Введіть назву курсу: ").strip()
    if not course_name:
        print("Помилка: Назва курсу не може бути порожньою!")
        return

    instructor = input("Введіть викладача курсу: ").strip()
    if not instructor:
        print("Помилка: Ім'я викладача не може бути порожнім!")
        return

    course_id = database.add_course(course_name, instructor)
    print(f"Успішно додано курс! ID: {course_id}")


def edit_student_ui():
    print("\n--- Редагування даних студента ---")
    list_students_ui()
    try:
        student_id = int(input("\nВведіть ID студента для редагування: ").strip())
    except ValueError:
        print("Помилка: ID має бути числом!")
        return

    student = database.get_student_by_id(student_id)
    if not student:
        print(f"Студента з ID {student_id} не знайдено!")
        return

    print(f"Поточні дані: Ім'я={student['name']}, Вік={student['age']}, Спеціальність={student['major']}")
    new_name = input(f"Нове ім'я [{student['name']}]: ").strip() or student['name']
    
    age_str = input(f"Новий вік [{student['age']}]: ").strip()
    new_age = int(age_str) if age_str else student['age']

    new_major = input(f"Нова спеціальність [{student['major']}]: ").strip() or student['major']

    if database.update_student(student_id, new_name, new_age, new_major):
        print("Дані студента успішно оновлено!")
    else:
        print("Не вдалося оновити дані студента.")


def edit_course_ui():
    print("\n--- Редагування даних курсу ---")
    list_courses_ui()
    try:
        course_id = int(input("\nВведіть ID курсу для редагування: ").strip())
    except ValueError:
        print("Помилка: ID має бути числом!")
        return

    course = database.get_course_by_id(course_id)
    if not course:
        print(f"Курс з ID {course_id} не знайдено!")
        return

    print(f"Поточні дані: Назва={course['course_name']}, Викладач={course['instructor']}")
    new_name = input(f"Нова назва [{course['course_name']}]: ").strip() or course['course_name']
    new_instructor = input(f"Новий викладач [{course['instructor']}]: ").strip() or course['instructor']

    if database.update_course(course_id, new_name, new_instructor):
        print("Дані курсу успішно оновлено!")
    else:
        print("Не вдалося оновити дані курсу.")


def enroll_student_ui():
    print("\n--- Запис студента на курс ---")
    list_students_ui()
    try:
        student_id = int(input("\nВведіть ID студента: ").strip())
    except ValueError:
        print("Помилка: Некоректний ID студента!")
        return

    student = database.get_student_by_id(student_id)
    if not student:
        print(f"Студента з ID {student_id} не знайдено!")
        return

    list_courses_ui()
    try:
        course_id = int(input("\nВведіть ID курсу: ").strip())
    except ValueError:
        print("Помилка: Некоректний ID курсу!")
        return

    course = database.get_course_by_id(course_id)
    if not course:
        print(f"Курс з ID {course_id} не знайдено!")
        return

    if database.enroll_student(student_id, course_id):
        print(f"Студента '{student['name']}' успішно зараховано на курс '{course['course_name']}'!")
    else:
        print("Студент вже записаний на цей курс або виникла помилка.")


def filter_students_by_course_ui():
    print("\n--- Фільтрація: Студенти на конкретному курсі ---")
    list_courses_ui()
    try:
        course_id = int(input("\nВведіть ID курсу для перегляду списку студентів: ").strip())
    except ValueError:
        print("Помилка: Некоректний ID курсу!")
        return

    course = database.get_course_by_id(course_id)
    if not course:
        print(f"Курс з ID {course_id} не знайдено!")
        return

    students = database.get_students_in_course(course_id)
    print(f"\nКурс: {course['course_name']} (Викладач: {course['instructor']})")
    print(f"Зареєстровано студентів: {len(students)}")
    headers = ["ID", "ПІБ / Ім'я", "Вік", "Спеціальність"]
    rows = [[s["id"], s["name"], s["age"], s["major"]] for s in students]
    print_table(headers, rows)


def view_student_courses_ui():
    print("\n--- Перегляд курсів студента ---")
    list_students_ui()
    try:
        student_id = int(input("\nВведіть ID студента: ").strip())
    except ValueError:
        print("Помилка: Некоректний ID!")
        return

    student = database.get_student_by_id(student_id)
    if not student:
        print(f"Студента з ID {student_id} не знайдено!")
        return

    courses = database.get_courses_for_student(student_id)
    print(f"\nСтудент: {student['name']} ({student['major']})")
    headers = ["ID Курсу", "Назва курсу", "Викладач"]
    rows = [[c["course_id"], c["course_name"], c["instructor"]] for c in courses]
    print_table(headers, rows)


def main():
    database.init_db()
    # Populate with sample initial data if DB is empty
    database.seed_sample_data()

    while True:
        print("\n=============================================")
        print("   ЖУРНАЛ СТУДЕНТІВ ТА КУРСІВ УНІВЕРСИТЕТУ   ")
        print("=============================================")
        print("1. Переглянути всіх студентів")
        print("2. Переглянути всі курси")
        print("3. Додати нового студента")
        print("4. Додати новий курс")
        print("5. Редагувати дані студента")
        print("6. Редагувати дані курсу")
        print("7. Зареєструвати студента на курс")
        print("8. Переглянути студентів на конкретному курсі (Фільтр)")
        print("9. Переглянути курси конкретного студента")
        print("0. Вихід")
        print("---------------------------------------------")

        choice = input("Оберіть пункт меню (0-9): ").strip()

        if choice == "1":
            list_students_ui()
        elif choice == "2":
            list_courses_ui()
        elif choice == "3":
            add_student_ui()
        elif choice == "4":
            add_course_ui()
        elif choice == "5":
            edit_student_ui()
        elif choice == "6":
            edit_course_ui()
        elif choice == "7":
            enroll_student_ui()
        elif choice == "8":
            filter_students_by_course_ui()
        elif choice == "9":
            view_student_courses_ui()
        elif choice == "0":
            print("Дякуємо за використання системи! До побачення.")
            sys.exit(0)
        else:
            print("Некоректний вибір. Спробуйте ще раз!")


if __name__ == "__main__":
    main()
