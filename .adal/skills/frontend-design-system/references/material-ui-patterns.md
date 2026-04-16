# Material UI (MUI) Design Patterns

## Installation
```bash
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
```

## Theme Setup
```tsx
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'

const theme = createTheme({
  palette: {
    mode: 'light', // or 'dark'
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {/* Your app */}
    </ThemeProvider>
  )
}
```

## Common Components

### Button
```tsx
import Button from '@mui/material/Button'

<Button variant="contained">Contained</Button>
<Button variant="outlined">Outlined</Button>
<Button variant="text">Text</Button>

<Button color="primary">Primary</Button>
<Button color="secondary">Secondary</Button>
<Button color="error">Error</Button>
<Button color="success">Success</Button>

<Button size="small">Small</Button>
<Button size="medium">Medium</Button>
<Button size="large">Large</Button>
```

### Card
```tsx
import Card from '@mui/material/Card'
import CardHeader from '@mui/material/CardHeader'
import CardContent from '@mui/material/CardContent'
import CardActions from '@mui/material/CardActions'

<Card sx={{ maxWidth: 345 }}>
  <CardHeader
    title="Card Title"
    subheader="Subheader"
  />
  <CardContent>
    <Typography>Content here</Typography>
  </CardContent>
  <CardActions>
    <Button size="small">Action</Button>
  </CardActions>
</Card>
```

### TextField
```tsx
import TextField from '@mui/material/TextField'

<TextField label="Task Title" variant="outlined" fullWidth />
<TextField label="Description" multiline rows={4} />
<TextField type="date" label="Due Date" InputLabelProps={{ shrink: true }} />
```

### Dialog
```tsx
import Dialog from '@mui/material/Dialog'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'

<Dialog open={open} onClose={handleClose}>
  <DialogTitle>Dialog Title</DialogTitle>
  <DialogContent>
    <TextField label="Input" fullWidth />
  </DialogContent>
  <DialogActions>
    <Button onClick={handleClose}>Cancel</Button>
    <Button onClick={handleSave}>Save</Button>
  </DialogActions>
</Dialog>
```

### Chip (Badge)
```tsx
import Chip from '@mui/material/Chip'

<Chip label="High Priority" color="error" />
<Chip label="Work" variant="outlined" />
<Chip label="Completed" color="success" onDelete={handleDelete} />
```

### List
```tsx
import List from '@mui/material/List'
import ListItem from '@mui/material/ListItem'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemIcon from '@mui/material/ListItemIcon'
import ListItemText from '@mui/material/ListItemText'
import Checkbox from '@mui/material/Checkbox'

<List>
  {tasks.map((task) => (
    <ListItem key={task.id}>
      <ListItemButton>
        <ListItemIcon>
          <Checkbox edge="start" />
        </ListItemIcon>
        <ListItemText primary={task.title} secondary={task.description} />
      </ListItemButton>
    </ListItem>
  ))}
</List>
```

### Tabs
```tsx
import Tabs from '@mui/material/Tabs'
import Tab from '@mui/material/Tab'
import Box from '@mui/material/Box'

<Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
  <Tabs value={value} onChange={handleChange}>
    <Tab label="All" />
    <Tab label="Active" />
    <Tab label="Completed" />
  </Tabs>
</Box>
```

### Date Picker
```bash
npm install @mui/x-date-pickers
```

```tsx
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns'

<LocalizationProvider dateAdapter={AdapterDateFns}>
  <DatePicker
    label="Due Date"
    value={date}
    onChange={setDate}
  />
</LocalizationProvider>
```

### Select
```tsx
import Select from '@mui/material/Select'
import MenuItem from '@mui/material/MenuItem'
import FormControl from '@mui/material/FormControl'
import InputLabel from '@mui/material/InputLabel'

<FormControl fullWidth>
  <InputLabel>Priority</InputLabel>
  <Select value={priority} onChange={handleChange} label="Priority">
    <MenuItem value="high">High</MenuItem>
    <MenuItem value="medium">Medium</MenuItem>
    <MenuItem value="low">Low</MenuItem>
  </Select>
</FormControl>
```

### Snackbar (Toast)
```tsx
import Snackbar from '@mui/material/Snackbar'
import Alert from '@mui/material/Alert'

<Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
  <Alert onClose={handleClose} severity="success">
    Task created successfully!
  </Alert>
</Snackbar>
```

## Layout Patterns

### Container
```tsx
import Container from '@mui/material/Container'

<Container maxWidth="lg">
  {/* Content */}
</Container>
```

### Grid System
```tsx
import Grid from '@mui/material/Grid'

<Grid container spacing={2}>
  <Grid item xs={12} md={6} lg={4}>
    <Card>Item 1</Card>
  </Grid>
  <Grid item xs={12} md={6} lg={4}>
    <Card>Item 2</Card>
  </Grid>
</Grid>
```

### Stack (Flexbox)
```tsx
import Stack from '@mui/material/Stack'

<Stack direction="row" spacing={2}>
  <Button>Button 1</Button>
  <Button>Button 2</Button>
</Stack>

<Stack direction="column" spacing={3}>
  <Card>Card 1</Card>
  <Card>Card 2</Card>
</Stack>
```

## Styling with sx prop
```tsx
<Box
  sx={{
    width: 300,
    height: 300,
    backgroundColor: 'primary.main',
    '&:hover': {
      backgroundColor: 'primary.dark',
    },
    borderRadius: 2,
    p: 2, // padding: theme.spacing(2)
    mt: 4, // marginTop: theme.spacing(4)
  }}
>
  Content
</Box>
```

## Dark Mode
```tsx
import { useTheme } from '@mui/material/styles'
import useMediaQuery from '@mui/material/useMediaQuery'

const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)')

const theme = createTheme({
  palette: {
    mode: prefersDarkMode ? 'dark' : 'light',
  },
})
```
