import { createTheme, PaletteColor } from '@mui/material/styles';

declare module '@mui/material/styles' {
  interface Palette {
    whatsapp: PaletteColor;
    facebook: PaletteColor;
    instagram: PaletteColor;
  }
  interface PaletteOptions {
    whatsapp?: PaletteColor;
    facebook?: PaletteColor;
    instagram?: PaletteColor;
  }
}

export const theme = createTheme({
  palette: {
    primary: {
      main: '#3b82f6',
      light: '#eff6ff',
      dark: '#1d4ed8',
    },
    secondary: {
      main: '#6b7280',
    },
    background: {
      default: '#f9fafb',
      paper: '#ffffff',
    },
    whatsapp: {
      main: '#25d366',
      light: '#4ade80',
      dark: '#16a34a',
      contrastText: '#ffffff',
    },
    facebook: {
      main: '#1877f2',
      light: '#3b82f6',
      dark: '#1d4ed8',
      contrastText: '#ffffff',
    },
    instagram: {
      main: '#e4405f',
      light: '#f472b6',
      dark: '#be185d',
      contrastText: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2rem',
      fontWeight: 700,
    },
    h2: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: '8px',
          },
        },
      },
    },
  },
});
