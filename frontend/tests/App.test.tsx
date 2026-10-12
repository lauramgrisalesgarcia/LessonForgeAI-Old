import { describe, it, expect } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import App from '../src/App';

describe('App component', () => {
  it('renderiza el encabezado de la aplicación', () => {
    render(<App />);
    expect(screen.getByRole('heading', { level: 1, name: 'LessonForge AI' })).toBeInTheDocument();
  });

  it('cambia el rol activo al pulsar "Vista Estudiante"', () => {
    render(<App />);
    expect(screen.getByText('Docente', { selector: 'strong' })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Vista Estudiante' }));

    expect(screen.getByText('Estudiante', { selector: 'strong' })).toBeInTheDocument();
  });
});
