import { describe, it, expect } from 'vitest';
import React from 'react';
import App from '../src/App';

describe('App component', () => {
  it('se exporta e instancia como componente válido de React', () => {
    expect(App).toBeDefined();
    const element = React.createElement(App);
    expect(React.isValidElement(element)).toBe(true);
  });
});
