/**
 * StudyTrack Frontend Application Engine
 * Pure Vanilla JavaScript (No React / Frameworks)
 */

const API_BASE = window.location.origin;

// Application State
const state = {
    students: [],
    courses: [],
    currentTab: 'dashboard'
};

// DOM Initialization
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initStudentForm();
    initCourseForm();
    initControls();
    initRosterEventDelegation();
    initAlgorithmsTab();
    initAIHelperPanel();
    
    // Initial Load
    fetchStudents();
    fetchCourses();
});

/* ==========================================================================
   Error Banner & Toast Notification System
   ========================================================================== */
function showError(message) {
    const banner = document.getElementById('error-banner');
    if (banner) {
        banner.textContent = `Error: ${message}`;
        banner.style.display = 'block';
        setTimeout(() => {
            banner.style.display = 'none';
        }, 6000);
    }
    showToast(message, 'error');
}

function clearError() {
    const banner = document.getElementById('error-banner');
    if (banner) banner.style.display = 'none';
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let iconSvg = '';
    if (type === 'success') {
        iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
    } else if (type === 'error') {
        iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
    } else {
        iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
    }

    toast.innerHTML = `${iconSvg} <span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

/* ==========================================================================
   Tab Navigation Handler
   ========================================================================== */
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const pages = document.querySelectorAll('.tab-page');
    const pageTitle = document.getElementById('page-title');
    const pageSubtitle = document.getElementById('page-subtitle');

    const meta = {
        'dashboard': { title: 'Student Roster Management', subtitle: 'Manage student profiles, edit ages, view roster, and filter records' },
        'courses': { title: 'Course Offerings', subtitle: 'Register, assign, and manage academic courses' },
        'algorithms': { title: 'Algorithms & Report', subtitle: 'Custom Insertion Sort, Binary Search, and API Report endpoint' },
        'ai-helper': { title: 'AI Helper & Study Notes Panel', subtitle: 'Note summarizer & Cosine Similarity vector search across 5 CS notes' }
    };

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');
            state.currentTab = targetTab;

            navItems.forEach(nav => nav.classList.remove('active'));
            pages.forEach(page => page.classList.remove('active'));

            item.classList.add('active');
            const activePage = document.getElementById(`tab-${targetTab}`);
            if (activePage) activePage.classList.add('active');

            if (meta[targetTab]) {
                pageTitle.textContent = meta[targetTab].title;
                pageSubtitle.textContent = meta[targetTab].subtitle;
            }
        });
    });
}

/* ==========================================================================
   Part 1: Student CRUD Operations
   ========================================================================== */
async function fetchStudents(minAge = null) {
    const rosterList = document.getElementById('roster-list');
    if (!rosterList) return;

    rosterList.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading student roster...</p>
        </div>`;

    try {
        let url = `${API_BASE}/students/`;
        if (minAge !== null && minAge !== undefined && minAge !== '') {
            url += `?min_age=${encodeURIComponent(minAge)}`;
        }

        const response = await fetch(url);
        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || 'Failed to fetch student records');
        }

        state.students = await response.json();
        renderStudentsGrid(state.students);
        updateHeaderStats();
        populateStudentDropdown(state.students);
        clearError();
    } catch (err) {
        showError(err.message);
    }
}

function updateHeaderStats() {
    const totalStudentsEl = document.getElementById('stat-total-students');
    const avgAgeEl = document.getElementById('stat-avg-age');

    if (totalStudentsEl) totalStudentsEl.textContent = state.students.length;

    if (!state.students || state.students.length === 0) {
        if (avgAgeEl) avgAgeEl.textContent = '0';
        return;
    }

    const totalAge = state.students.reduce((sum, s) => sum + s.age, 0);
    const avg = (totalAge / state.students.length).toFixed(1);
    if (avgAgeEl) avgAgeEl.textContent = avg;
}

function createStudentCardElement(student) {
    const card = document.createElement('div');
    card.className = 'student-card';
    card.setAttribute('data-id', student.id);

    const initial = student.name.charAt(0).toUpperCase();

    card.innerHTML = `
        <div class="card-top">
            <div class="avatar-circle">${escapeHtml(initial)}</div>
            <span class="badge badge-info">ID #${student.id}</span>
        </div>
        <div class="card-info">
            <div class="student-name-text">${escapeHtml(student.name)}</div>
            <div class="student-email-text">${escapeHtml(student.email)}</div>
        </div>
        <div class="age-editor-row">
            <span class="age-label">Current Age:</span>
            <input type="number" class="age-input-field" value="${student.age}" min="1" max="120" id="age-input-${student.id}">
        </div>
        <div class="card-bottom-actions">
            <button class="btn btn-save btn-sm btn-save-age" data-id="${student.id}">
                Save Age
            </button>
            <button class="btn btn-danger btn-sm btn-delete-student" data-id="${student.id}">
                Delete
            </button>
        </div>
    `;
    return card;
}

function renderStudentsGrid(studentsList) {
    const rosterList = document.getElementById('roster-list');
    if (!rosterList) return;
    rosterList.innerHTML = '';

    if (!studentsList || studentsList.length === 0) {
        rosterList.innerHTML = `
            <div class="loading-state">
                <p>No student records found in roster.</p>
            </div>`;
        return;
    }

    studentsList.forEach(student => {
        const card = createStudentCardElement(student);
        rosterList.appendChild(card);
    });
}

function initStudentForm() {
    const form = document.getElementById('student-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const nameInput = document.getElementById('student-name');
        const emailInput = document.getElementById('student-email');
        const ageInput = document.getElementById('student-age');
        const btn = document.getElementById('btn-add-student');

        const payload = {
            name: nameInput.value.trim(),
            email: emailInput.value.trim(),
            age: parseInt(ageInput.value, 10)
        };

        btn.disabled = true;

        try {
            const response = await fetch(`${API_BASE}/students/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                const detailMsg = Array.isArray(errData.detail) ? errData.detail.map(d => d.msg).join(', ') : (errData.detail || 'Failed to add student');
                throw new Error(detailMsg);
            }

            const newStudent = await response.json();
            
            // Append new card directly using DOM element creation
            const rosterList = document.getElementById('roster-list');
            const newCard = createStudentCardElement(newStudent);
            
            if (rosterList.querySelector('.loading-state')) {
                rosterList.innerHTML = '';
            }
            rosterList.appendChild(newCard);

            state.students.push(newStudent);
            updateHeaderStats();
            populateStudentDropdown(state.students);

            showToast(`Student ${newStudent.name} registered successfully!`, 'success');
            form.reset();
            clearError();
        } catch (err) {
            showError(err.message);
        } finally {
            btn.disabled = false;
        }
    });
}

/* ==========================================================================
   Event Delegation on #roster-list
   ========================================================================== */
function initRosterEventDelegation() {
    const rosterList = document.getElementById('roster-list');
    if (!rosterList) return;

    rosterList.addEventListener('click', async (e) => {
        // Save Age Button Click
        const saveBtn = e.target.closest('.btn-save-age');
        if (saveBtn) {
            const studentId = parseInt(saveBtn.getAttribute('data-id'), 10);
            await handlePatchAge(studentId);
            return;
        }

        // Delete Student Button Click
        const deleteBtn = e.target.closest('.btn-delete-student');
        if (deleteBtn) {
            const studentId = parseInt(deleteBtn.getAttribute('data-id'), 10);
            await handleDeleteStudent(studentId);
            return;
        }
    });
}

/* ==========================================================================
   Edit Age via PATCH /students/{student_id}
   ========================================================================== */
async function handlePatchAge(studentId) {
    const ageInput = document.getElementById(`age-input-${studentId}`);
    if (!ageInput) return;

    const newAge = parseInt(ageInput.value, 10);
    if (isNaN(newAge) || newAge <= 0) {
        showError('Please enter a valid age greater than 0.');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/students/${studentId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ age: newAge })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || 'Failed to update student age');
        }

        const updatedStudent = await response.json();
        showToast(`Age for ${updatedStudent.name} updated to ${updatedStudent.age}!`, 'success');
        
        const idx = state.students.findIndex(s => s.id === studentId);
        if (idx !== -1) state.students[idx].age = updatedStudent.age;
        updateHeaderStats();
        clearError();
    } catch (err) {
        showError(err.message);
    }
}

async function handleDeleteStudent(studentId) {
    if (!confirm(`Are you sure you want to delete Student ID #${studentId}?`)) return;

    try {
        const response = await fetch(`${API_BASE}/students/${studentId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || 'Failed to delete student');
        }

        const card = document.querySelector(`.student-card[data-id="${studentId}"]`);
        if (card) card.remove();

        state.students = state.students.filter(s => s.id !== studentId);
        updateHeaderStats();
        populateStudentDropdown(state.students);
        showToast(`Student ID #${studentId} deleted successfully.`, 'info');
        clearError();
    } catch (err) {
        showError(err.message);
    }
}

/* ==========================================================================
   Course Management (CRUD)
   ========================================================================== */
async function fetchCourses() {
    const list = document.getElementById('courses-list');
    if (!list) return;

    try {
        const response = await fetch(`${API_BASE}/courses/`);
        if (!response.ok) throw new Error('Failed to fetch course records');

        state.courses = await response.json();
        renderCoursesGrid(state.courses);
    } catch (err) {
        showError(err.message);
    }
}

function populateStudentDropdown(studentsList) {
    const select = document.getElementById('course-student-id');
    if (!select) return;
    select.innerHTML = '<option value="">-- Optional: Select Student --</option>';
    studentsList.forEach(student => {
        const opt = document.createElement('option');
        opt.value = student.id;
        opt.textContent = `${student.name} (ID #${student.id})`;
        select.appendChild(opt);
    });
}

function renderCoursesGrid(coursesList) {
    const list = document.getElementById('courses-list');
    if (!list) return;
    list.innerHTML = '';

    if (!coursesList || coursesList.length === 0) {
        list.innerHTML = `<div class="loading-state"><p>No course offerings registered.</p></div>`;
        return;
    }

    coursesList.forEach(course => {
        const card = document.createElement('div');
        card.className = 'course-card';
        card.setAttribute('data-id', course.id);

        const student = state.students.find(s => s.id === course.student_id);
        const studentText = student ? `${student.name} (ID #${student.id})` : 'Unassigned';

        card.innerHTML = `
            <div class="card-top">
                <div class="course-code-badge">${course.credits} Credits</div>
                <span class="badge badge-purple">Course ID #${course.id}</span>
            </div>
            <div class="card-info">
                <div class="course-title-text">${escapeHtml(course.course_name)}</div>
            </div>
            <div class="age-editor-row">
                <span class="age-label">Enrolled Student:</span>
                <span class="badge badge-info">${escapeHtml(studentText)}</span>
            </div>
            <div class="card-bottom-actions">
                <button class="btn btn-danger btn-sm" onclick="handleDeleteCourse(${course.id})">
                    Delete Course
                </button>
            </div>
        `;
        list.appendChild(card);
    });
}

function initCourseForm() {
    const form = document.getElementById('course-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const nameInput = document.getElementById('course-name');
        const creditsInput = document.getElementById('course-credits');
        const studentSelect = document.getElementById('course-student-id');
        const btn = document.getElementById('btn-add-course');

        const studentIdVal = studentSelect.value ? parseInt(studentSelect.value, 10) : null;
        const creditsVal = parseInt(creditsInput.value, 10);

        if (creditsVal < 1 || creditsVal > 6) {
            showError('Course credits must be between 1 and 6 inclusive.');
            return;
        }

        const payload = {
            course_name: nameInput.value.trim(),
            credits: creditsVal,
            student_id: studentIdVal
        };

        btn.disabled = true;

        try {
            const response = await fetch(`${API_BASE}/courses/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || 'Failed to add course');
            }

            const newCourse = await response.json();
            showToast(`Course "${newCourse.course_name}" created successfully!`, 'success');
            form.reset();
            fetchCourses();
            clearError();
        } catch (err) {
            showError(err.message);
        } finally {
            btn.disabled = false;
        }
    });
}

async function handleDeleteCourse(courseId) {
    if (!confirm(`Are you sure you want to delete Course ID #${courseId}?`)) return;

    try {
        const response = await fetch(`${API_BASE}/courses/${courseId}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to delete course');

        showToast(`Course ID #${courseId} deleted.`, 'info');
        fetchCourses();
    } catch (err) {
        showError(err.message);
    }
}

/* ==========================================================================
   Controls, Filters, Sorting & Binary Search
   ========================================================================== */
function initControls() {
    // Sort by Age Button
    const btnSortAge = document.getElementById('btn-sort-age');
    if (btnSortAge) {
        btnSortAge.addEventListener('click', async () => {
            try {
                const response = await fetch(`${API_BASE}/students/sorted?by=age`);
                if (!response.ok) throw new Error('Failed to sort roster by age');
                const sorted = await response.json();
                renderStudentsGrid(sorted);
                showToast('Roster sorted by Age using custom Insertion Sort!', 'success');
                clearError();
            } catch (err) {
                showError(err.message);
            }
        });
    }

    // Sort by Name Button
    const btnSortName = document.getElementById('btn-sort-name');
    if (btnSortName) {
        btnSortName.addEventListener('click', async () => {
            try {
                const response = await fetch(`${API_BASE}/students/sorted?by=name`);
                if (!response.ok) throw new Error('Failed to sort roster by name');
                const sorted = await response.json();
                renderStudentsGrid(sorted);
                showToast('Roster sorted by Name using custom Insertion Sort!', 'success');
                clearError();
            } catch (err) {
                showError(err.message);
            }
        });
    }

    // Binary Search by Name Button
    const btnBinarySearch = document.getElementById('btn-binary-search');
    const searchInput = document.getElementById('binary-search-input');
    if (btnBinarySearch && searchInput) {
        btnBinarySearch.addEventListener('click', async () => {
            const query = searchInput.value.trim();
            if (!query) {
                showError('Please enter a name to search using Binary Search.');
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/students/search?name=${encodeURIComponent(query)}`);
                if (!response.ok) {
                    const errData = await response.json().catch(() => ({}));
                    throw new Error(errData.detail || `No student found matching '${query}'`);
                }
                const matches = await response.json();
                renderStudentsGrid(matches);
                showToast(`Binary Search found ${matches.length} matching student(s)!`, 'success');
                clearError();
            } catch (err) {
                showError(err.message);
            }
        });
    }

    // Min Age Filter Button
    const btnApplyMinAge = document.getElementById('btn-apply-min-age');
    const minAgeInput = document.getElementById('min-age-filter-input');
    if (btnApplyMinAge && minAgeInput) {
        btnApplyMinAge.addEventListener('click', () => {
            const minAgeVal = minAgeInput.value ? parseInt(minAgeInput.value, 10) : null;
            fetchStudents(minAgeVal);
        });
    }

    // Reset Roster Button
    const btnReset = document.getElementById('btn-reset-roster');
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            if (minAgeInput) minAgeInput.value = '';
            if (searchInput) searchInput.value = '';
            fetchStudents();
        });
    }
}

/* ==========================================================================
   Report Endpoint Handler
   ========================================================================== */
function initAlgorithmsTab() {
    const btnReport = document.getElementById('btn-generate-report');
    const minAgeInput = document.getElementById('report-min-age-input');
    const reportOutput = document.getElementById('report-output');
    const countOutput = document.getElementById('report-count-output');

    if (btnReport) {
        btnReport.addEventListener('click', async () => {
            const minAge = minAgeInput ? parseInt(minAgeInput.value, 10) : 21;
            try {
                const response = await fetch(`${API_BASE}/students/report?min_age=${minAge}`);
                if (!response.ok) throw new Error('Failed to generate student report');
                const data = await response.json();
                
                if (countOutput) countOutput.textContent = data.count_meeting_min_age;
                if (reportOutput) reportOutput.textContent = data.raw_text || data.report.join('\n');
                showToast(`Report generated! (${data.count_meeting_min_age} students meeting min age ${minAge})`, 'success');
                clearError();
            } catch (err) {
                showError(err.message);
            }
        });
    }
}

/* ==========================================================================
   AI Helper Panel Engine
   ========================================================================== */
function initAIHelperPanel() {
    // 1. Note Summarizer (POST /assistant/summarize)
    const btnSummarize = document.getElementById('btn-summarize');
    const notesInput = document.getElementById('ai-notes-input');
    const resultsCard = document.getElementById('summary-results-card');

    if (btnSummarize && notesInput) {
        btnSummarize.addEventListener('click', async () => {
            const text = notesInput.value;
            btnSummarize.disabled = true;

            try {
                const response = await fetch(`${API_BASE}/assistant/summarize`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });

                if (!response.ok) throw new Error('Note summarizer failed');
                const data = await response.json();

                document.getElementById('summary-topic').textContent = data.topic;
                document.getElementById('summary-difficulty').textContent = data.difficulty;
                
                const pointsList = document.getElementById('summary-key-points');
                if (pointsList) {
                    pointsList.innerHTML = (data.key_points || []).map(pt => `<li>${escapeHtml(pt)}</li>`).join('');
                }

                if (resultsCard) resultsCard.style.display = 'block';
                showToast('Note summarized successfully!', 'success');
                clearError();
            } catch (err) {
                showError(err.message);
            } finally {
                btnSummarize.disabled = false;
            }
        });
    }

    // 2. Semantic Search Notes (GET /assistant/search?query=)
    const btnSearchNotes = document.getElementById('btn-search-notes');
    const queryInput = document.getElementById('ai-search-query');
    const resultsList = document.getElementById('search-results-list');

    if (btnSearchNotes && queryInput) {
        btnSearchNotes.addEventListener('click', async () => {
            const query = queryInput.value.trim();
            btnSearchNotes.disabled = true;

            try {
                const response = await fetch(`${API_BASE}/assistant/search?query=${encodeURIComponent(query)}`);
                if (!response.ok) throw new Error('Note semantic search failed');
                const notes = await response.json();

                if (resultsList) {
                    resultsList.innerHTML = '';
                    notes.forEach(note => {
                        const item = document.createElement('div');
                        item.className = 'note-item';
                        item.innerHTML = `
                            <div class="note-item-header">
                                <span>Note #${note.id}: ${escapeHtml(note.title)}</span>
                                <span class="score-badge">Cosine Score: ${note.score}</span>
                            </div>
                            <p class="card-desc" style="margin-bottom:0;">${escapeHtml(note.content)}</p>
                        `;
                        resultsList.appendChild(item);
                    });
                }

                showToast('Semantic Search calculated Cosine Similarity scores!', 'success');
                clearError();
            } catch (err) {
                showError(err.message);
            } finally {
                btnSearchNotes.disabled = false;
            }
        });
    }
}

// Utility: HTML escaping
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
