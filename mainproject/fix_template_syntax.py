
import os

file_path = r'c:\Users\HP\OneDrive\Desktop\HMS\Hospital_Management\mainproject\templates\appointment_list.html'

content = r"""{% extends base_template|default:'base.html' %}

{% block title %}Appointments | MediCore AI{% endblock %}
{% block page_title %}Appointments{% endblock %}

{% block extra_css %}
<style>
    .appt-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 32px;
    }

    .search-group {
        display: flex;
        gap: 12px;
        flex: 1;
        max-width: 400px;
    }

    .filter-btn {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 10px 20px;
        border-radius: 12px;
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-muted);
        display: flex;
        align-items: center;
        gap: 10px;
        transition: 0.2s;
    }

    .filter-btn:hover {
        border-color: var(--primary);
        color: var(--primary);
    }

    .appt-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
        gap: 28px;
    }

    .appt-card {
        background: white;
        border-radius: 20px;
        border: 1px solid #f1f5f9;
        padding: 28px;
        display: flex;
        flex-direction: column;
        gap: 24px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .appt-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.05);
        border-color: #cbd5e1;
    }

    .status-ribbon {
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: #e2e8f0;
    }

    .status-confirmed-ribbon {
        background: #22c55e;
    }

    .status-completed-ribbon {
        background: #94a3b8;
    }

    .appt-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .status-badge {
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .status-confirmed-text {
        color: #15803d;
    }

    .status-completed-text {
        color: #64748b;
    }

    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

    .dot-confirmed {
        background: #22c55e;
        box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.1);
    }

    .dot-completed {
        background: #94a3b8;
    }

    .appt-time-info {
        text-align: right;
        color: var(--text-main);
    }

    .date-row {
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 2px;
        display: flex;
        align-items: center;
        gap: 8px;
        justify-content: flex-end;
    }

    .time-row {
        font-size: 0.85rem;
        color: var(--text-muted);
        font-weight: 600;
    }

    .patient-row {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .p-avatar {
        width: 52px;
        height: 52px;
        border-radius: 16px;
        background: #f1f5f9;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.1rem;
        color: var(--primary);
    }

    .p-name-main {
        font-weight: 800;
        font-size: 1.1rem;
        color: var(--text-main);
        margin-bottom: 2px;
    }

    .p-meta-sub {
        font-size: 0.85rem;
        color: var(--text-muted);
        font-weight: 500;
    }

    .clinical-brief {
        background: #f8fafc;
        border-radius: 12px;
        padding: 16px 20px;
    }

    .brief-label {
        font-size: 0.7rem;
        font-weight: 800;
        color: #94a3b8;
        text-transform: uppercase;
        margin-bottom: 8px;
        letter-spacing: 0.05em;
    }

    .brief-text {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-main);
    }

    .vitals-summary {
        background: #f0fdf4;
        border: 1px solid #dcfce7;
        border-radius: 16px;
        padding: 20px;
    }

    .vitals-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
    }

    .vital-item {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 0.85rem;
        color: #1e293b;
    }

    .vital-item i {
        color: #94a3b8;
        font-size: 1rem;
    }

    .vital-item b {
        font-weight: 700;
    }

    .btn-action-group {
        display: flex;
        gap: 12px;
    }

    .btn-primary-soft {
        flex: 1;
        background: var(--primary);
        color: white;
        border: none;
        padding: 14px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        transition: all 0.2s;
        text-decoration: none;
        text-align: center;
    }

    .btn-primary-soft:hover {
        background: var(--primary-hover);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }

    .btn-outline-soft {
        background: white;
        border: 1px solid #e2e8f0;
        color: var(--text-main);
        padding: 14px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        transition: 0.2s;
        text-decoration: none;
        text-align: center;
    }

    .btn-outline-soft:hover {
        background: #f8fafc;
        border-color: #cbd5e1;
    }
</style>
{% endblock %}

{% block content %}
<div class="appt-controls">
    <form class="search-group" method="GET">
        <div class="flex-grow-1 position-relative">
            <i class="fas fa-search position-absolute top-50 start-0 translate-middle-y ms-3 text-muted"></i>
            <input type="text" name="q" value="{{ query }}"
                class="form-control border-0 bg-white rounded-pill ps-5 py-2 shadow-sm"
                placeholder="Search patient name...">
        </div>
        <select name="status" class="form-select border-0 bg-white rounded-pill px-4 shadow-sm w-auto fw-bold"
            onchange="this.form.submit()">
            <option value="">All Status</option>
            <option value="CONFIRMED" {% if status_filter == 'CONFIRMED' %}selected{% endif %}>Confirmed</option>
            <option value="PENDING" {% if status_filter == 'PENDING' %}selected{% endif %}>Pending</option>
            <option value="COMPLETED" {% if status_filter == 'COMPLETED' %}selected{% endif %}>Completed</option>
        </select>
        {% if query or status_filter %}
        <a href="{% url 'appointment_list' %}" class="btn btn-light rounded-pill px-4 shadow-sm border-0">
            <i class="fas fa-times me-1"></i> Clear
        </a>
        {% endif %}
    </form>
    <a href="#" class="btn btn-primary rounded-pill px-4 fw-bold shadow-sm">
        <i class="fas fa-plus me-2"></i> New Appointment
    </a>
</div>

<div class="appt-grid">
    {% for appt in appointments %}
    <div class="appt-card">
        <div
            class="status-ribbon {% if appt.status == 'CONFIRMED' %}status-confirmed-ribbon{% elif appt.status == 'COMPLETED' %}status-completed-ribbon{% endif %}">
        </div>

        <div class="appt-header">
            <div
                class="status-badge {% if appt.status == 'CONFIRMED' %}status-confirmed-text{% elif appt.status == 'COMPLETED' %}status-completed-text{% endif %}">
                <div
                    class="dot {% if appt.status == 'CONFIRMED' %}dot-confirmed{% elif appt.status == 'COMPLETED' %}dot-completed{% endif %}">
                </div>
                {{ appt.status }}
            </div>
            <div class="appt-time-info">
                <div class="date-row">
                    <i class="far fa-calendar-alt"></i>
                    {{ appt.appointment_date|date:"M d, Y" }}
                </div>
                <div class="time-row">
                    <i class="far fa-clock"></i>
                    {{ appt.appointment_time|time:"H:i" }}
                </div>
            </div>
        </div>

        <div class="patient-row">
            <div class="p-avatar">{{ appt.patient.name|truncatechars:1|upper }}</div>
            <div class="p-info">
                <div class="p-name-main">{{ appt.patient.name }}</div>
                <div class="p-meta-sub">ID: #P{{ appt.patient.id }} • Patient</div>
            </div>
        </div>

        <div class="clinical-brief">
            <div class="brief-label">Chief Complaint</div>
            <div class="brief-text">{{ appt.reason|default:"General Health Screening" }}</div>
        </div>

        {% with triage=appt.triagequeue_set.first %}
        {% if triage %}
        <div class="vitals-summary">
            <div class="vitals-header mb-3">
                <span class="badge bg-white text-success border border-success-subtle rounded-pill">
                    <i class="fas fa-heartbeat me-1"></i> Triage Vitals
                </span>
            </div>
            <div class="vitals-grid">
                <div class="vital-item">
                    <i class="fas fa-wave-square"></i> BP: <b>{{ triage.blood_pressure|default:"--" }}</b>
                </div>
                <div class="vital-item">
                    <i class="fas fa-thermometer-half"></i> Temp: <b>{{ triage.temperature|default:"--" }}°F</b>
                </div>
                <div class="vital-item">
                    <i class="fas fa-heart"></i> HR: <b>{{ triage.pulse_rate|default:"--" }} bpm</b>
                </div>
                <div class="vital-item">
                    <i class="fas fa-weight"></i> Wt: <b>{{ triage.weight|default:"--" }} kg</b>
                </div>
            </div>
        </div>
        {% endif %}
        {% endwith %}

        {% if request.user.role != 'PATIENT' %}
        <div class="btn-action-group">
            <a href="{% url 'patient_list' %}?p={{ appt.patient.id }}" class="btn-outline-soft flex-1">
                <i class="fas fa-user-circle me-1"></i> Profile
            </a>
            {% if appt.status != 'COMPLETED' %}
            <form action="{% url 'complete_appointment' appt.id %}" method="POST" class="flex-1 d-flex">
                {% csrf_token %}
                <button type="submit" class="btn-primary-soft w-100 border-0">
                    <i class="fas fa-check-circle me-1"></i> Complete
                </button>
            </form>
            {% else %}
            <button class="btn-outline-soft flex-1" disabled>
                <i class="fas fa-check text-success me-1"></i> Completed
            </button>
            {% endif %}
        </div>
        {% endif %}
    </div>
    {% empty %}
    <div class="col-12 text-center py-5">
        <div class="bg-light d-inline-block rounded-circle p-4 mb-4">
            <i class="fas fa-calendar-times fa-3x text-muted opacity-20"></i>
        </div>
        <h4 class="fw-bold text-muted">No Scheduled Appointments</h4>
        <p class="text-muted">New appointments will appear here once booked by patients or staff.</p>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""

print(f"Writing to {file_path}")
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Write complete.")
