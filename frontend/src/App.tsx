import React, { useState } from 'react';

export const App: React.FC = () => {
  const [role, setRole] = useState<'teacher' | 'student'>('teacher');

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, sans-serif', padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <header style={{ borderBottom: '1px solid #e5e7eb', paddingBottom: '1rem', marginBottom: '2rem' }}>
        <h1 style={{ color: '#1e3a8a', margin: 0 }}>LessonForge AI</h1>
        <p style={{ color: '#4b5563', marginTop: '0.5rem' }}>
          Plataforma de refuerzo para aprendizaje de idiomas con IA
        </p>
      </header>

      <main>
        <section style={{ backgroundColor: '#f9fafb', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
          <h2>Panel Inicial de Demostración</h2>
          <p>
            Rol activo seleccionado: <strong>{role === 'teacher' ? 'Docente' : 'Estudiante'}</strong>
          </p>

          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
            <button
              onClick={() => setRole('teacher')}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: role === 'teacher' ? '#2563eb' : '#e5e7eb',
                color: role === 'teacher' ? '#ffffff' : '#1f2937',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Vista Docente
            </button>
            <button
              onClick={() => setRole('student')}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: role === 'student' ? '#2563eb' : '#e5e7eb',
                color: role === 'student' ? '#ffffff' : '#1f2937',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Vista Estudiante
            </button>
          </div>
        </section>

        <section style={{ marginTop: '2rem', color: '#6b7280', fontSize: '0.875rem' }}>
          <p>Estado del sistema: Estructura base inicializada y lista para implementación de servicios.</p>
        </section>
      </main>
    </div>
  );
};

export default App;
