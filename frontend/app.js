/**
 * StudyTrack Frontend Application Engine
 * Pure Vanilla JavaScript (No React / Frameworks)
 */

const API_BASE = window.location.origin;

// Application State
const state = {
    students: [],
    currentTab: 'dashboard',
    notes: []
};

// DOM Elements Initialization
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initStudentForm();
    initControls();
    initAlgorithmsTab();
    initAISummarizerTab();
    initSemanticSearchTab();
    
    // Initial Load
    fetchStudents();
    fetchNotesDataset();
});

/* ==========================================================================
   Toast Notification System
   ========================================================================== */
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
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
        'dashboard': { title: 'Student Dashboard', subtitle: 'Manage student profiles, edit ages, and view records' },
        'algorithms': { title: 'Algorithms & Report', subtitle: 'Custom Insertion Sort, Binary Search, and API Report endpoint' },
        'ai-summarizer': { title: 'AI Text Summarizer', subtitle: 'Extract topics, key points, and difficulty metrics into structured JSON' },
        'semantic-search': { title: 'Semantic Search Engine', subtitle: 'Cosine Similarity vector search across computer science note dataset' }
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
   Part 1: Core Student Management (CRUD)
   ========================================================================== */
async function fetchStudents() {
    const grid = document.getElementById('students-grid');
    grid.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading student profiles from database...</p>
        </div>`;

    try {
        const response = await fetch(`${API_BASE}/api/students`);
        if (!response.ok) throw new Error('Failed to fetch student records');
        
        state.students = await response.json();
        renderStudentsGrid(state.students);
        updateHeaderStats(state.students);
        document.getElementById('active-filter-badge').style.display = 'none';
        document.getElementById('btn-reset-search').style.display = 'none';
    } catch (err) {
        grid.innerHTML = `<div class="loading-state"><p style="color: var(--danger)">Error: ${escapeHtml(err.message)}</p></div>`;
        showToast(err.message, 'error');
    }
}

function updateHeaderStats(studentsList) {
    const totalEl = document.getElementById('stat-total-students');
    const avgAgeEl = document.getElementById('stat-avg-age');

    totalEl.textContent = studentsList.length;

    if (studentsList.length === 0) {
        avgAgeEl.textContent = '0';
        return;
    }

    const totalAge = studentsList.reduce((sum, s) => sum + s.age, 0);
    const avg = (totalAge / studentsList.length).toFixed(1);
    avgAgeEl.textContent = avg;
}

function renderStudentsGrid(studentsList) {
    const grid = document.getElementById('students-grid');
    grid.innerHTML = '';

    if (!studentsList || studentsList.length === 0) {
        grid.innerHTML = `
            <div class="loading-state">
                <p>No student records found. Add a new student above!</p>
            </div>`;
        return;
    }

    studentsList.forEach(student => {
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
                <button class="btn btn-save btn-sm" onclick="handleSaveAge(${student.id})">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    Save Age
                </button>
                <button class="btn btn-danger btn-sm" onclick="handleDeleteStudent(${student.id})">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    Delete
                </button>
            </div>
        `;
        grid.appendChild(card);
    });
}

function initStudentForm() {
    const form = document.getElementById('add-student-form');
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
        btn.innerHTML = `<div class="spinner" style="width:16px;height:16px;border-width:2px;"></div> Saving...`;

        try {
            const response = await fetch(`${API_BASE}/api/students`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to add student');
            }

            const newStudent = await response.json();
            showToast(`Student ${newStudent.name} added successfully!`, 'success');
            form.reset();
            fetchStudents();
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                Add Student`;
        }
    });
}

async function handleSaveAge(studentId) {
    const ageInput = document.getElementById(`age-input-${studentId}`);
    const newAge = parseInt(ageInput.value, 10);

    if (isNaN(newAge) || newAge < 1 || newAge > 120) {
        showToast('Please enter a valid age between 1 and 120.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/students/${studentId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ age: newAge })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Failed to update student age');
        }

        const updatedStudent = await response.json();
        showToast(`Updated age for ${updatedStudent.name} to ${updatedStudent.age}!`, 'success');
        fetchStudents();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function handleDeleteStudent(studentId) {
    if (!confirm('Are you sure you want to delete this student profile?')) return;

    try {
        const response = await fetch(`${API_BASE}/api/students/${studentId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Failed to delete student');
        }

        showToast(`Student ID #${studentId} deleted successfully.`, 'info');
        fetchStudents();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function initControls() {
    // Refresh Button
    document.getElementById('btn-refresh-students').addEventListener('click', fetchStudents);

    // Insertion Sort Button
    document.getElementById('btn-insertion-sort').addEventListener('click', async () => {
        try {
            const response = await fetch(`${API_BASE}/api/students/sorted-by-age`);
            if (!response.ok) throw new Error('Failed to run insertion sort');

            const sortedStudents = await response.json();
            renderStudentsGrid(sortedStudents);
            document.getElementById('active-filter-badge').style.display = 'inline-block';
            document.getElementById('active-filter-badge').textContent = 'Sorted by Age (Insertion Sort)';
            document.getElementById('btn-reset-search').style.display = 'inline-block';
            showToast('Students sorted by Age using custom Insertion Sort!', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    // Binary Search Handler
    const searchInput = document.getElementById('binary-search-input');
    const searchBtn = document.getElementById('btn-binary-search');
    const resetBtn = document.getElementById('btn-reset-search');

    const handleBinarySearch = async () => {
        const query = searchInput.value.trim();
        if (!query) {
            showToast('Please enter a name to search using Binary Search.', 'info');
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/api/students/search?name=${encodeURIComponent(query)}`);
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'No student found');
            }

            const matches = await response.json();
            renderStudentsGrid(matches);
            document.getElementById('active-filter-badge').style.display = 'inline-block';
            document.getElementById('active-filter-badge').textContent = `Binary Search Match: "${query}"`;
            resetBtn.style.display = 'inline-block';
            showToast(`Binary Search found ${matches.length} matching student(s)!`, 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    };

    searchBtn.addEventListener('click', handleBinarySearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleBinarySearch();
    });

    resetBtn.addEventListener('click', () => {
        searchInput.value = '';
        fetchStudents();
    });
}

/* ==========================================================================
   Part 2: Algorithms & Report
   ========================================================================== */
function initAlgorithmsTab() {
    const reportBtn = document.getElementById('btn-generate-report');
    const reportBox = document.getElementById('report-output');

    reportBtn.addEventListener('click', async () => {
        reportBox.innerHTML = '<div class="spinner" style="margin: 20px auto;"></div>';

        try {
            const response = await fetch(`${API_BASE}/api/report`);
            if (!response.ok) throw new Error('Failed to generate report');

            const data = await response.json();
            reportBox.textContent = data.raw_text || data.formatted_report.join('\n');
            showToast('Report endpoint successfully generated!', 'success');
        } catch (err) {
            reportBox.textContent = `Error: ${err.message}`;
            showToast(err.message, 'error');
        }
    });
}

/* ==========================================================================
   Part 3: AI Assistant Features
   ========================================================================== */
function initAISummarizerTab() {
    const inputArea = document.getElementById('summarizer-input');
    const runBtn = document.getElementById('btn-run-summary');
    const sampleBtn = document.getElementById('btn-sample-summary');
    const resultsContainer = document.getElementById('summary-results');

    sampleBtn.addEventListener('click', () => {
        inputArea.value = `Binary search is an efficient divide and conquer algorithm for finding an item from a sorted list of items. It works by repeatedly dividing in half the portion of the list that could contain the item until you have narrowed down the possible locations to just one. The time complexity of binary search is O(log n), making it exponentially faster than linear search for large datasets.`;
    });

    runBtn.addEventListener('click', async () => {
        const text = inputArea.value.trim();
        if (text.length < 5) {
            showToast('Please enter a longer text to summarize.', 'info');
            return;
        }

        runBtn.disabled = true;
        runBtn.innerHTML = `<div class="spinner" style="width:16px;height:16px;border-width:2px;"></div> Summarizing...`;

        try {
            const response = await fetch(`${API_BASE}/api/ai/summarize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (!response.ok) throw new Error('Failed to generate text summary');

            const data = await response.json();

            // Populate UI
            document.getElementById('summary-topic').textContent = data.topic;
            
            const diffBadge = document.getElementById('summary-difficulty-badge');
            diffBadge.textContent = data.difficulty;
            diffBadge.className = `badge ${data.difficulty === 'Easy' ? 'badge-green' : data.difficulty === 'Medium' ? 'badge-purple' : 'badge-pink'}`;

            const list = document.getElementById('summary-key-points-list');
            list.innerHTML = data.key_points.map(pt => `<li>${escapeHtml(pt)}</li>`).join('');

            document.getElementById('summary-raw-json').textContent = JSON.stringify(data, null, 2);

            resultsContainer.style.display = 'block';
            showToast('Text summarized successfully!', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            runBtn.disabled = false;
            runBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                Summarize Text`;
        }
    });
}

async function fetchNotesDataset() {
    try {
        const response = await fetch(`${API_BASE}/api/ai/notes`);
        if (response.ok) {
            state.notes = await response.json();
            renderSemanticNotes(state.notes.map(n => ({ ...n, similarity_score: 0.0 })));
        }
    } catch (err) {
        console.error('Notes dataset fetch error:', err);
    }
}

function initSemanticSearchTab() {
    const searchInput = document.getElementById('semantic-search-input');
    const searchBtn = document.getElementById('btn-run-semantic-search');
    const chips = document.querySelectorAll('.chip-btn');

    const handleSearch = async (queryText) => {
        const query = queryText || searchInput.value.trim();
        if (!query) {
            showToast('Please enter a search query for semantic analysis.', 'info');
            return;
        }

        searchBtn.disabled = true;
        searchBtn.innerHTML = `<div class="spinner" style="width:16px;height:16px;border-width:2px;"></div> Searching...`;

        try {
            const response = await fetch(`${API_BASE}/api/ai/semantic-search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            if (!response.ok) throw new Error('Semantic search failed');

            const results = await response.json();
            renderSemanticNotes(results);
            showToast('Cosine Similarity calculated across notes dataset!', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            searchBtn.disabled = false;
            searchBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                Search Notes`;
        }
    };

    searchBtn.addEventListener('click', () => handleSearch());
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });

    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const q = chip.getAttribute('data-query');
            searchInput.value = q;
            handleSearch(q);
        });
    });
}

function renderSemanticNotes(notesList) {
    const container = document.getElementById('semantic-search-results');
    container.innerHTML = '';

    notesList.forEach(note => {
        const card = document.createElement('div');
        card.className = 'note-card';

        const scorePercent = (note.similarity_score * 100).toFixed(1);

        card.innerHTML = `
            <div class="note-header">
                <div class="note-title">Note #${note.id}: ${escapeHtml(note.title)}</div>
                <div class="similarity-bar-wrapper">
                    <div class="similarity-bar-bg">
                        <div class="similarity-bar-fill" style="width: ${scorePercent}%"></div>
                    </div>
                    <span class="similarity-val">${scorePercent}%</span>
                </div>
            </div>
            <p class="card-desc" style="margin-bottom:0;">${escapeHtml(note.content)}</p>
        `;
        container.appendChild(card);
    });
}

// Utility: HTML escape
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
