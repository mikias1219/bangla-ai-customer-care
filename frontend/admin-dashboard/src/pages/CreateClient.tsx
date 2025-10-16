import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert
} from '@mui/material';
import { adminApi, Client } from '../lib/api';

interface CreateClientProps {
  onBack: () => void;
  onCreated: () => void;
}

function CreateClient({ onBack, onCreated }: CreateClientProps) {
  const [formData, setFormData] = useState({
    business_name: '',
    business_email: '',
    business_phone: '',
    business_address: '',
    contact_person: '',
    contact_email: '',
    contact_phone: '',
    business_type: '',
    website_url: '',
    facebook_page_url: '',
    instagram_username: '',
    subscription_plan: 'pay_as_you_go',
    language_preference: 'bn'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await adminApi.createClient(formData);
      setSuccess(true);
      setTimeout(() => {
        onCreated();
        onBack();
      }, 2000);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to create client');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  if (success) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h5" color="success.main" gutterBottom>
            ✓ Client Created Successfully!
          </Typography>
          <Typography variant="body1" sx={{ mb: 2 }}>
            The client account has been created and is ready to use.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Redirecting to client list...
          </Typography>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 2 }}>
        <Button variant="outlined" onClick={onBack}>
          ← Back to Clients
        </Button>
      </Box>

      <Paper sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom>
          Create New Client
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Add a new business client to the platform
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            {/* Business Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Business Information
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="Business Name"
                value={formData.business_name}
                onChange={(e) => handleChange('business_name', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="Business Email"
                type="email"
                value={formData.business_email}
                onChange={(e) => handleChange('business_email', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Business Phone"
                value={formData.business_phone}
                onChange={(e) => handleChange('business_phone', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Business Type</InputLabel>
                <Select
                  value={formData.business_type}
                  onChange={(e) => handleChange('business_type', e.target.value)}
                >
                  <MenuItem value="restaurant">Restaurant</MenuItem>
                  <MenuItem value="hotel">Hotel</MenuItem>
                  <MenuItem value="retail">Retail/E-commerce</MenuItem>
                  <MenuItem value="service">Service Provider</MenuItem>
                  <MenuItem value="other">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Business Address"
                multiline
                rows={2}
                value={formData.business_address}
                onChange={(e) => handleChange('business_address', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Website URL"
                value={formData.website_url}
                onChange={(e) => handleChange('website_url', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Language Preference</InputLabel>
                <Select
                  value={formData.language_preference}
                  onChange={(e) => handleChange('language_preference', e.target.value)}
                >
                  <MenuItem value="bn">Bangla</MenuItem>
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="banglish">Banglish</MenuItem>
                  <MenuItem value="all">All Languages</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Contact Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Contact Person Information
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contact Person Name"
                value={formData.contact_person}
                onChange={(e) => handleChange('contact_person', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contact Email"
                type="email"
                value={formData.contact_email}
                onChange={(e) => handleChange('contact_email', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contact Phone"
                value={formData.contact_phone}
                onChange={(e) => handleChange('contact_phone', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Subscription Plan</InputLabel>
                <Select
                  value={formData.subscription_plan}
                  onChange={(e) => handleChange('subscription_plan', e.target.value)}
                >
                  <MenuItem value="pay_as_you_go">Pay as You Go (৳0.75 per reply)</MenuItem>
                  <MenuItem value="basic">Basic (৳3,999/month - 500 customers)</MenuItem>
                  <MenuItem value="standard">Standard (৳7,499/month - 1000 customers)</MenuItem>
                  <MenuItem value="premium">Premium (৳17,999/month - 2500 customers)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Social Media */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Social Media Integration (Optional)
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Facebook Page URL"
                value={formData.facebook_page_url}
                onChange={(e) => handleChange('facebook_page_url', e.target.value)}
                placeholder="https://facebook.com/yourpage"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Instagram Username"
                value={formData.instagram_username}
                onChange={(e) => handleChange('instagram_username', e.target.value)}
                placeholder="@yourusername"
              />
            </Grid>

            {/* Submit */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{ minWidth: 120 }}
                >
                  {loading ? 'Creating...' : 'Create Client'}
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={onBack}
                  disabled={loading}
                >
                  Cancel
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
}

export default CreateClient;
