use std::collections::HashMap;
use chrono::{DateTime, Utc};

// Structure to hold blood sugar readings
#[derive(Debug, Clone)]
struct BloodSugarReading {
    value: f32,
    timestamp: DateTime<Utc>,
}

// Structure to hold medication information
#[derive(Debug, Clone)]
struct Medication {
    name: String,
    dosage: String,
    frequency: String,
}

// Structure to hold appointment information
#[derive(Debug, Clone)]
struct Appointment {
    date: DateTime<Utc>,
    doctor: String,
    appointment_type: String,
}

// Main structure to hold all health data
#[derive(Debug)]
struct HealthData {
    blood_sugar_readings: Vec<BloodSugarReading>,
    medications: Vec<Medication>,
    appointments: Vec<Appointment>,
}

impl HealthData {
    // Create a new HealthData instance
    fn new() -> Self {
        HealthData {
            blood_sugar_readings: Vec::new(),
            medications: Vec::new(),
            appointments: Vec::new(),
        }
    }

    // Add a blood sugar reading
    fn add_blood_sugar(&mut self, value: f32, timestamp: DateTime<Utc>) {
        self.blood_sugar_readings.push(BloodSugarReading { value, timestamp });
    }

    // Add a medication
    fn add_medication(&mut self, name: String, dosage: String, frequency: String) {
        self.medications.push(Medication {
            name,
            dosage,
            frequency,
        });
    }

    // Add an appointment
    fn add_appointment(&mut self, date: DateTime<Utc>, doctor: String, appointment_type: String) {
        self.appointments.push(Appointment {
            date,
            doctor,
            appointment_type,
        });
    }

    // Calculate average blood sugar
    fn average_blood_sugar(&self) -> Option<f32> {
        if self.blood_sugar_readings.is_empty() {
            return None;
        }
        let sum: f32 = self.blood_sugar_readings.iter().map(|r| r.value).sum();
        Some(sum / self.blood_sugar_readings.len() as f32)
    }

    // Get blood sugar statistics
    fn blood_sugar_stats(&self) -> Option<(f32, f32, f32)> {
        if self.blood_sugar_readings.is_empty() {
            return None;
        }
        let values: Vec<f32> = self.blood_sugar_readings.iter().map(|r| r.value).collect();
        let min = values.iter().fold(f32::INFINITY, |a, &b| a.min(b));
        let max = values.iter().fold(f32::NEG_INFINITY, |a, &b| a.max(b));
        let avg = self.average_blood_sugar().unwrap_or(0.0);
        Some((min, max, avg))
    }

    // Get upcoming appointments
    fn upcoming_appointments(&self, days: i64) -> Vec<&Appointment> {
        let now = Utc::now();
        self.appointments
            .iter()
            .filter(|apt| (apt.date - now).num_days() <= days)
            .collect()
    }
}

fn main() {
    // Create a new HealthData instance
    let mut health_data = HealthData::new();

    // Add some sample data
    health_data.add_blood_sugar(120.0, Utc::now());
    health_data.add_blood_sugar(115.0, Utc::now());
    health_data.add_blood_sugar(125.0, Utc::now());

    health_data.add_medication(
        "Metformin".to_string(),
        "500mg".to_string(),
        "Twice daily".to_string(),
    );

    // Print some statistics
    if let Some((min, max, avg)) = health_data.blood_sugar_stats() {
        println!("Blood Sugar Statistics:");
        println!("Minimum: {:.1}", min);
        println!("Maximum: {:.1}", max);
        println!("Average: {:.1}", avg);
    }

    // Print medications
    println!("\nMedications:");
    for med in &health_data.medications {
        println!("{} - {} ({})", med.name, med.dosage, med.frequency);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::{Duration, Utc};

    #[test]
    fn test_blood_sugar_stats() {
        let mut health_data = HealthData::new();
        
        // Add test readings
        health_data.add_blood_sugar(100.0, Utc::now());
        health_data.add_blood_sugar(120.0, Utc::now());
        health_data.add_blood_sugar(140.0, Utc::now());

        let stats = health_data.blood_sugar_stats().unwrap();
        assert_eq!(stats.0, 100.0); // min
        assert_eq!(stats.1, 140.0); // max
        assert_eq!(stats.2, 120.0); // avg
    }

    #[test]
    fn test_empty_blood_sugar_stats() {
        let health_data = HealthData::new();
        assert!(health_data.blood_sugar_stats().is_none());
    }

    #[test]
    fn test_medication_management() {
        let mut health_data = HealthData::new();
        
        health_data.add_medication(
            "Insulin".to_string(),
            "10 units".to_string(),
            "Before meals".to_string(),
        );

        assert_eq!(health_data.medications.len(), 1);
        assert_eq!(health_data.medications[0].name, "Insulin");
        assert_eq!(health_data.medications[0].dosage, "10 units");
        assert_eq!(health_data.medications[0].frequency, "Before meals");
    }

    #[test]
    fn test_upcoming_appointments() {
        let mut health_data = HealthData::new();
        let now = Utc::now();
        
        // Add appointments
        health_data.add_appointment(
            now + Duration::days(1),
            "Dr. Smith".to_string(),
            "Check-up".to_string(),
        );
        health_data.add_appointment(
            now + Duration::days(5),
            "Dr. Johnson".to_string(),
            "Follow-up".to_string(),
        );
        health_data.add_appointment(
            now + Duration::days(10),
            "Dr. Brown".to_string(),
            "Annual".to_string(),
        );

        let upcoming = health_data.upcoming_appointments(3);
        assert_eq!(upcoming.len(), 1); // Only the appointment within 3 days
        assert_eq!(upcoming[0].doctor, "Dr. Smith");
    }
}
