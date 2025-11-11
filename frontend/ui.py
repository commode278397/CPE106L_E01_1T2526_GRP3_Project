import re
import flet as ft
import requests

API_BASE_URL = "http://127.0.0.1:8000"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def main(page: ft.Page):
    page.title = "SkillBridge Portal"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 25

    def post_json(path: str, payload: dict):
        """Send POST to API and return (ok, data or error message)."""
        try:
            resp = requests.post(f"{API_BASE_URL}{path}", json=payload)
            if resp.ok:
                return True, resp.json()
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            return False, detail
        except Exception as exc:
            return False, f"Could not contact API: {exc}"

    # ---------- Registration Tab ----------

    name_field = ft.TextField(label="Name", width=350)
    email_field = ft.TextField(label="Email", width=350)
    skills_field = ft.TextField(
        label="Skills (comma-separated)",
        width=350,
        hint_text="e.g. tutoring, carpentry",
    )
    registration_result = ft.Text()

    def register_clicked(e):
        name = (name_field.value or "").strip()
        email = (email_field.value or "").strip()
        skills = (skills_field.value or "").strip()

        if not name:
            registration_result.value = "Please enter your name."
            registration_result.color = "red"
        elif not email or not EMAIL_RE.match(email):
            registration_result.value = "Enter a valid email address."
            registration_result.color = "red"
        else:
            ok, data = post_json(
                "/users",
                {"name": name, "email": email, "skills": skills or None},
            )
            if ok:
                registration_result.value = (
                    f"Volunteer created: {data['name']} (ID {data['id']})"
                )
                registration_result.color = "green"
                name_field.value = ""
                email_field.value = ""
                skills_field.value = ""
            else:
                registration_result.value = f"Registration failed: {data}"
                registration_result.color = "red"
        page.update()

    registration_section = ft.Column(
        [
            ft.Text("Add a new volunteer profile.", size=16),
            name_field,
            email_field,
            skills_field,
            ft.ElevatedButton("Register", on_click=register_clicked),
            registration_result,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.START,
        spacing=15,
    )

    # ---------- Offer Skill Section ----------

    offer_user_id = ft.TextField(label="Volunteer ID", width=200)
    offer_skill_field = ft.TextField(label="Skill", width=350)
    offer_result = ft.Text()

    def offer_skill_clicked(e):
        user_id_raw = (offer_user_id.value or "").strip()
        skill = (offer_skill_field.value or "").strip()
        if not user_id_raw.isdigit():
            offer_result.value = "Volunteer ID must be a number."
            offer_result.color = "red"
        elif not skill:
            offer_result.value = "Skill cannot be empty."
            offer_result.color = "red"
        else:
            ok, data = post_json(
                f"/volunteers/{int(user_id_raw)}/skills",
                {"skill": skill},
            )
            if ok:
                offer_result.value = (
                    f"Skill '{data['skill']}' offered by volunteer {data['user_id']}."
                )
                offer_result.color = "green"
                offer_skill_field.value = ""
            else:
                offer_result.value = f"Offer failed: {data}"
                offer_result.color = "red"
        page.update()

    offer_section = ft.Column(
        [
            ft.Text("Advertise a volunteer skill for matching.", size=16),
            offer_user_id,
            offer_skill_field,
            ft.ElevatedButton("Offer Skill", on_click=offer_skill_clicked),
            offer_result,
        ],
        spacing=15,
    )

    # ---------- Create Request Section ----------

    request_title = ft.TextField(label="Title", width=350)
    request_desc = ft.TextField(
        label="Description",
        width=350,
        multiline=True,
        min_lines=2,
        max_lines=4,
    )
    request_skills = ft.TextField(
        label="Required Skills",
        width=350,
        hint_text="e.g. plumbing, tutoring",
    )
    requester_name = ft.TextField(label="Requester Name", width=350)
    requester_location = ft.TextField(label="Location", width=350)
    request_result = ft.Text()

    def create_request_clicked(e):
        payload = {
            "title": (request_title.value or "").strip(),
            "description": (request_desc.value or "").strip() or None,
            "required_skills": (request_skills.value or "").strip() or None,
            "requester_name": (requester_name.value or "").strip(),
            "location": (requester_location.value or "").strip(),
        }

        if not payload["title"]:
            request_result.value = "Title is required."
            request_result.color = "red"
        elif not payload["requester_name"]:
            request_result.value = "Requester name is required."
            request_result.color = "red"
        elif not payload["location"]:
            request_result.value = "Location is required."
            request_result.color = "red"
        else:
            ok, data = post_json("/requests", payload)
            if ok:
                request_result.value = (
                    f"Request #{data['id']} created with status {data['status']}."
                )
                request_result.color = "green"
                request_title.value = ""
                request_desc.value = ""
                request_skills.value = ""
                requester_name.value = ""
                requester_location.value = ""
            else:
                request_result.value = f"Request failed: {data}"
                request_result.color = "red"
        page.update()

    request_section = ft.Column(
        [
            ft.Text("Post a new help request.", size=16),
            request_title,
            request_desc,
            request_skills,
            requester_name,
            requester_location,
            ft.ElevatedButton("Submit Request", on_click=create_request_clicked),
            request_result,
        ],
        spacing=15,
    )

    # ---------- Accept Request Section ----------

    accept_request_id = ft.TextField(label="Request ID", width=200)
    accept_volunteer_id = ft.TextField(label="Volunteer ID", width=200)
    accept_result = ft.Text()

    def accept_clicked(e):
        req_id = (accept_request_id.value or "").strip()
        vol_id = (accept_volunteer_id.value or "").strip()
        if not req_id.isdigit():
            accept_result.value = "Request ID must be numeric."
            accept_result.color = "red"
        elif not vol_id.isdigit():
            accept_result.value = "Volunteer ID must be numeric."
            accept_result.color = "red"
        else:
            ok, data = post_json(
                f"/requests/{int(req_id)}/accept",
                {"volunteer_id": int(vol_id)},
            )
            if ok:
                accept_result.value = (
                    f"Volunteer {data['volunteer_id']} accepted request "
                    f"{data['request_id']} (status {data['status']})."
                )
                accept_result.color = "green"
            else:
                accept_result.value = f"Accept failed: {data}"
                accept_result.color = "red"
        page.update()

    accept_section = ft.Column(
        [
            ft.Text("Match a volunteer to a request.", size=16),
            accept_request_id,
            accept_volunteer_id,
            ft.ElevatedButton("Accept Request", on_click=accept_clicked),
            accept_result,
        ],
        spacing=15,
    )

    # ---------- Cancel Request Section ----------

    cancel_request_id = ft.TextField(label="Request ID", width=200)
    cancel_result = ft.Text()

    def cancel_clicked(e):
        req_id = (cancel_request_id.value or "").strip()
        if not req_id.isdigit():
            cancel_result.value = "Request ID must be numeric."
            cancel_result.color = "red"
        else:
            ok, data = post_json(f"/requests/{int(req_id)}/cancel", {})
            if ok:
                cancel_result.value = (
                    f"Request {data['id']} cancelled (status {data['status']})."
                )
                cancel_result.color = "green"
            else:
                cancel_result.value = f"Cancel failed: {data}"
                cancel_result.color = "red"
        page.update()

    cancel_section = ft.Column(
        [
            ft.Text("Withdraw an existing request.", size=16),
            cancel_request_id,
            ft.ElevatedButton("Cancel Request", on_click=cancel_clicked),
            cancel_result,
        ],
        spacing=15,
    )

    overview_section = ft.Column(
        [
            ft.Text("SkillBridge Control Center", size=22, weight="bold"),
            ft.Text(
                "Use the buttons above to navigate between key SkillBridge actions.",
                width=500,
            ),
            ft.Divider(),
            ft.Text("Tips:", weight="bold"),
            ft.Text("• Keep the FastAPI backend running on 127.0.0.1:8000."),
            ft.Text("• Note the volunteer ID after registration for future actions."),
            ft.Text("• A request cannot be matched once it is cancelled."),
        ],
        spacing=10,
    )

    sections = {
        "Overview": overview_section,
        "Register": registration_section,
        "Offer Skill": offer_section,
        "Create Request": request_section,
        "Accept Request": accept_section,
        "Cancel Request": cancel_section,
    }

    content_holder = ft.Container(
        content=sections["Overview"], padding=ft.padding.symmetric(vertical=10)
    )

    def navigate(e):
        label = e.control.data
        content_holder.content = sections[label]
        for btn in nav_row.controls:
            btn.disabled = btn.data == label
        page.update()

    nav_row = ft.Row(
        [
            ft.ElevatedButton(
                label,
                data=label,
                on_click=navigate,
                disabled=(label == "Overview"),
            )
            for label in sections.keys()
        ],
        spacing=10,
    )

    page.add(
        ft.Column(
            [
                ft.Text("SkillBridge Portal", size=26, weight="bold"),
                nav_row,
                ft.Divider(),
                content_holder,
            ],
            expand=1,
        )
    )


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
