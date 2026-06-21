# Open Source Healthcare Systems
## Operational Workflows & System Flows Master Registry (`flows.md`)

This file contains the master directory of all clinical, administrative, financial, and analytics system flows within the integrated Care EMR, Odoo ERP, and Metabase BI platform. It serves as a comprehensive training index to guide real-world deployments and user onboarding.

---

## 1. Domain A: Governance & Organization Hierarchy

Care EMR implements a hierarchical governance model using self-referential organizations to represent state, district, and local body levels.

### FLOW-01: Creating a State Organization (e.g., Kerala)
*   **Layperson UI Flow**:
    1.  Log in as a Super Admin and navigate to **Organizations** in the sidebar.
    2.  Click **Add Organization**.
    3.  Enter the state name (e.g., `Kerala`) as the **Name**.
    4.  Select **Organization Type** as `State`.
    5.  Leave the **Parent Organization** blank.
    6.  Click **Submit**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Organization` (in `care/care/emr/models/organization.py`)
    *   **Database Write**: Inserts a row in the `emr_organization` table.
    *   **Key Fields**: `name="Kerala"`, `org_type="state"`, `parent_id=NULL`, `level_cache=0`.

### FLOW-02: Creating a District Organization (under the State)
*   **Layperson UI Flow**:
    1.  Go to **Organizations** and click **Add Organization**.
    2.  Enter the district name, e.g., `Ernakulam`.
    3.  Select **Organization Type** as `District`.
    4.  Set the **Parent Organization** to `Kerala`.
    5.  Click **Submit**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Organization`
    *   **Database Write**: Inserts in `emr_organization`.
    *   **Key Fields**: `name="Ernakulam"`, `org_type="district"`, `parent_id=[Kerala UUID]`, `level_cache=1`.
    *   **Automation**: Trigger `set_organization_cache()` which appends parent IDs into the `parent_cache` ArrayField: `parent_cache=[Kerala_ID]`.

### FLOW-03: Creating a Local Body Organization (under the District)
*   **Layperson UI Flow**:
    1.  Click **Add Organization**.
    2.  Enter the local body name, e.g., `Kochi Corporation`.
    3.  Select **Organization Type** as `Local Body`.
    4.  Set the **Parent Organization** to `Ernakulam`.
    5.  Click **Submit**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Organization`
    *   **Database Write**: Inserts in `emr_organization`.
    *   **Key Fields**: `name="Kochi Corporation"`, `org_type="local_body"`, `parent_id=[Ernakulam UUID]`, `level_cache=2`.
    *   **Cache Result**: `parent_cache=[Kerala_ID, Ernakulam_ID]`.

### FLOW-04: Creating a Health Department Organization (under the Local Body)
*   **Layperson UI Flow**:
    1.  Click **Add Organization**.
    2.  Enter `Health Department`.
    3.  Select **Organization Type** as `Department`.
    4.  Set the **Parent Organization** to `Kochi Corporation`.
    5.  Click **Submit**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Organization`
    *   **Key Fields**: `org_type="department"`, `parent_id=[Kochi Corporation UUID]`, `level_cache=3`.

### FLOW-05: Linking Geographic Governance Boundaries to Facilities
*   **Layperson UI Flow**:
    1.  Open the **Facility Configuration** page for your hospital.
    2.  Under **Geographic Boundaries**, select `Kochi Corporation` or `Health Department` as the governing body.
    3.  Click **Save**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Facility` (in `care/care/facility/models/facility.py`)
    *   **Key Fields**: `geo_organization_id=[Kochi Corporation UUID]`.
    *   **Trigger**: Invokes `sync_cache()`, copying the parent IDs into `geo_organization_cache` ArrayField for rapid spatial queries.

---

## 2. Domain B: Facility & Spatial Location Administration

### FLOW-06: Registering a Hospital / Clinical Facility
*   **Layperson UI Flow**:
    1.  Navigate to **Facilities** and click **Create Facility**.
    2.  Enter Name (e.g. `Ernakulam General Hospital`), Type (e.g. `District Hospital`), address, coordinates, and contact phone.
    3.  Click **Create**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Facility`
    *   **Database Table**: `facility_facility`
    *   **Key Fields**: `name`, `facility_type` (mapped to integers, e.g. 860 for District Hospital), `phone_number`.
    *   **Automation**: Automatically spawns a root `FacilityOrganization` record named "Administration" linked to the facility.

### FLOW-07: Creating a Dedicated Laboratory Facility (e.g. Govt Lab)
*   **Layperson UI Flow**:
    1.  Navigate to **Facilities** and click **Create Facility**.
    2.  Enter Name (e.g. `Govt Diagnostic Lab Kochi`).
    3.  Select **Facility Type** as `Govt Labs` or `Private Labs`.
    4.  Click **Create**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Facility`
    *   **Database Write**: Inserts in `facility_facility`.
    *   **Key Fields**: `facility_type=9` (Govt Labs) or `facility_type=10` (Private Labs).

### FLOW-08: Creating Building Wings / Blocks inside a Facility
*   **Layperson UI Flow**:
    1.  Open the facility dashboard and navigate to the **Locations** tab.
    2.  Click **Add Location**.
    3.  Enter name: `Block A`.
    4.  Select **Location Type** as `Building` or `Wing`.
    5.  Leave the **Parent Location** field empty.
    6.  Click **Submit**.
*   **Backend Technical Flow**:
    *   **Django Model**: `FacilityLocation` (in `care/care/emr/models/location.py`)
    *   **Database Table**: `emr_facilitylocation`
    *   **Key Fields**: `name="Block A"`, `parent_id=NULL`, `level_cache=0`, `root_location_id=NULL`.

### FLOW-09: Creating Wards & Rooms inside a Wing
*   **Layperson UI Flow**:
    1.  Go to **Locations** and click **Add Location**.
    2.  Enter name: `ICU Ward 2` or `Room 201`.
    3.  Select **Location Type** as `Ward` or `Room`.
    4.  Set the **Parent Location** to `Block A`.
    5.  Click **Submit**.
*   **Backend Technical Flow**:
    *   **Django Model**: `FacilityLocation`
    *   **Key Fields**: `name="ICU Ward 2"`, `parent_id=[Block A UUID]`, `level_cache=1`.
    *   **Auto-Calculations**: `root_location_id=[Block A UUID]`. Sets `parent.has_children = True`.

### FLOW-10: Registering Beds under a Room
*   **Layperson UI Flow**:
    1.  Click **Add Location**.
    2.  Enter name: `Bed 104`.
    3.  Select **Location Type** as `Bed`.
    4.  Set **Parent Location** to `Room 201` (or `ICU Ward 2`).
    5.  Set status as `Active` and operational status as `Unoccupied`.
    6.  Click **Submit**.
*   **Backend Technical Flow**:
    *   **Django Model**: `FacilityLocation`
    *   **Key Fields**: `name="Bed 104"`, `parent_id=[Room 201 UUID]`, `level_cache=2`.
    *   **FHIR Type Mapping**: `location_type` JSONField is set to track standard FHIR location metadata.

---

## 3. Domain C: User Management & Role Allotment

### FLOW-11: Creating a New System User Account
*   **Layperson UI Flow**:
    1.  Navigate to **Users** in the Admin panel and click **Add New User**.
    2.  Enter Username, First Name, Last Name, Email, Password, and Phone Number.
    3.  Click **Create User**.
*   **Backend Technical Flow**:
    *   **Django Model**: `User` (in `care/users/models.py`)
    *   **Odoo Integration**: Triggers real-time sync via FastAPI connector to replicate the user as a partner (`res.partner`) and user (`res.users`) in Odoo ERP.

### FLOW-12: Allotting Roles & Designations
*   **Layperson UI Flow**:
    1.  Open the User Profile page.
    2.  Under **Designations / Responsibilities**, select a designation (e.g. `Doctor`, `Nurse`, `Manager`).
    3.  Click **Assign Designation**.
*   **Backend Technical Flow**:
    *   **Django Model**: `User` profile mappings.
    *   **Designation Validation**: Enforces that role-based organizations require designation context assignments (`ROLE_ORG` configurations).

### FLOW-13: Linking Users to Geographic Organizations (`OrganizationUser`)
*   **Layperson UI Flow**:
    1.  Navigate to **Organizations** and click on `Health Department`.
    2.  Click **Add User**.
    3.  Select the User (e.g., `doctor1`) and allot a Role (e.g., `Clinical Manager`).
    4.  Click **Save**.
*   **Backend Technical Flow**:
    *   **Django Model**: `OrganizationUser` (in `care/care/emr/models/organization.py`)
    *   **Database Table**: `emr_organizationuser`
    *   **Key Fields**: `organization_id`, `user_id`, `role_id` (ForeignKey to `RoleModel`).

### FLOW-14: Linking Users to Facility Administration (`FacilityOrganizationUser`)
*   **Layperson UI Flow**:
    1.  Navigate to **Facilities** and open `Ernakulam General Hospital`.
    2.  Under **Internal Organizations**, select the `Administration` department.
    3.  Click **Link User**, choose the user, select the role (e.g., `Facility Admin`), and click **Save**.
*   **Backend Technical Flow**:
    *   **Django Model**: `FacilityOrganizationUser`
    *   **Database Table**: `emr_facilityorganizationuser`
    *   **Key Fields**: `organization_id` (points to `FacilityOrganization`), `user_id`, `role_id`.

---

## 4. Domain D: Scheduling & Appointment Booking

### FLOW-15: Creating Doctor Schedule Availability Slots
*   **Layperson UI Flow**:
    1.  A doctor logs in and navigates to the **Scheduling** tab on their profile.
    2.  Click **Create Schedule**.
    3.  Define date range, active days, session start/end times (e.g., 09:00 - 13:00), and slot duration (e.g., 15 minutes).
    4.  Click **Generate Slots**.
*   **Backend Technical Flow**:
    *   **Django Models**: `Schedule` and `TokenSlot` (in `care/care/emr/models/scheduling/`)
    *   **Database Table**: `emr_schedule`, `emr_tokenslot`
    *   **Key Fields**: `start_time`, `end_time`, `slot_duration`, `status="available"`.

### FLOW-16: Patient Appointment Booking (Token System)
*   **Layperson UI Flow**:
    1.  Navigate to a facility and select **Book Appointment**.
    2.  Select the clinical specialty or specific doctor.
    3.  Choose an available slot from the calendar.
    4.  Input the Patient details and click **Confirm Booking**. The system displays an appointment token number (e.g., Token #12).
*   **Backend Technical Flow**:
    *   **Django Model**: `TokenBooking`
    *   **Database Table**: `emr_tokenbooking`
    *   **State Machine Action**: Sets `TokenSlot.status = "booked"` and links `TokenBooking.patient_id` and `TokenBooking.slot_id`.

### FLOW-17: Appointment Check-In & Queue Management
*   **Layperson UI Flow**:
    1.  When the patient arrives, the receptionist opens the **Appointment Queue** panel.
    2.  Locate the patient's token and click **Check-in**.
    3.  The system transitions the patient’s status to "Waiting" in the doctor's queue.
*   **Backend Technical Flow**:
    *   **Django Model**: `TokenBooking`
    *   **Key Fields**: `status="waiting"`, `arrival_time=current_time`.
    *   **Queue Update**: Triggers updates on the `TokenQueue` and `TokenSubQueue` models.

---

## 5. Domain E: Clinical Patient Intake & Care

### FLOW-18: Patient Registration
*   **Layperson UI Flow**:
    1.  Go to `/patient` and click **Register Patient**.
    2.  Input demographic fields (Name, Gender, DOB, Phone, Address, ID Proof).
    3.  Click **Submit**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Patient` (in `care/care/emr/models/patient.py`)
    *   **Database Table**: `emr_patient`
    *   **Key Fields**: `name`, `gender`, `date_of_birth`, `phone_number`.

### FLOW-19: Creating a Patient Encounter (Admission / Consultation)
*   **Layperson UI Flow**:
    1.  Open the Patient profile and click **Create Encounter**.
    2.  Select **Encounter Type**: `Inpatient / Admission` or `Outpatient / Consultation`.
    3.  Select the **Admitting Doctor** and Facility.
    4.  Click **Confirm**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Encounter` (in `care/care/emr/models/encounter.py`)
    *   **Database Table**: `emr_encounter`
    *   **Key Fields**: `patient_id`, `status="active"`, `class` (e.g. inpatient), `facility_id`.

### FLOW-20: Assigning a Patient to a Bed (Encounter Location Association)
*   **Layperson UI Flow**:
    1.  Inside the active Encounter card, scroll to **Location / Bed Assignment**.
    2.  Click **Assign Bed**.
    3.  Select location `Block A > ICU Ward 2 > Bed 104`.
    4.  Confirm date/time and click **Save**.
*   **Backend Technical Flow**:
    *   **Django Model**: `FacilityLocationEncounter` (in `care/care/emr/models/location.py`)
    *   **Database Table**: `emr_facilitylocationencounter`
    *   **State Machine Action**: Sets `FacilityLocation.current_encounter_id = Encounter.id` (locks the bed).
    *   **Key Fields**: `encounter_id`, `location_id`, `start_datetime`.

### FLOW-21: Transferring a Patient to a Different Bed / Room
*   **Layperson UI Flow**:
    1.  Open the active Encounter dashboard.
    2.  Click **Transfer Bed**.
    3.  Select a new unoccupied bed (e.g. `Bed 105`).
    4.  Confirm transfer date/time and save.
*   **Backend Technical Flow**:
    *   **Actions**:
        1. Update existing `FacilityLocationEncounter` for `Bed 104` by setting `end_datetime = current_time`.
        2. Set `Bed 104.current_encounter_id = NULL` (releases the old bed).
        3. Insert new `FacilityLocationEncounter` for `Bed 105` with `start_datetime = current_time`.
        4. Set `Bed 105.current_encounter_id = Encounter.id` (locks the new bed).

### FLOW-22: Recording Clinical Vitals & Daily Rounds
*   **Layperson UI Flow**:
    1.  On the active patient profile, click **Log Vitals / Daily Round**.
    2.  Enter Pulse, Blood Pressure, Respiratory Rate, Temperature, and Consciousness Level.
    3.  Click **Save**.
*   **Backend Technical Flow**:
    *   **Django Model**: `DailyRound` (in `care/care/facility/models/patient.py`)
    *   **Key Fields**: `bp`, `pulse`, `temperature`, `consciousness_level`.

### FLOW-23: Discharging a Patient & Vacating Locations
*   **Layperson UI Flow**:
    1.  Open the active Encounter dashboard and click **Discharge Patient**.
    2.  Select discharge status (e.g., Recovered), enter notes, and confirm.
*   **Backend Technical Flow**:
    *   **Actions**:
        1. Set `Encounter.status = "completed"`.
        2. Set `FacilityLocationEncounter.end_datetime = discharge_time`.
        3. Set `FacilityLocation.current_encounter_id = NULL` (releases the bed).

---

## 6. Domain F: Medication, Allergy, & Consent Lifecycle

### FLOW-24: Prescribing Medication (Medication Request)
*   **Layperson UI Flow**:
    1.  During a consultation, the doctor opens the **Prescriptions** panel.
    2.  Click **Add Prescription**.
    3.  Search for and select a drug (e.g. `Paracetamol 500mg`).
    4.  Specify dosage (e.g. `1 tablet`), frequency (`TID` / three times a day), route (`Oral`), and duration (`5 days`).
    5.  Click **Prescribe**.
*   **Backend Technical Flow**:
    *   **Django Model**: `MedicationRequest` (in `care/care/emr/models/medication_request.py`)
    *   **Database Table**: `emr_medicationrequest`
    *   **Key Fields**: `patient_id`, `encounter_id`, `medication` (JSONField details), `dosage_instruction` (JSONField).

### FLOW-25: Recording Medication Administration (Nurse Workflow)
*   **Layperson UI Flow**:
    1.  The ward nurse opens the patient's active medication sheet.
    2.  Select the scheduled drug dose and click **Administer**.
    3.  Verify the drug, dose, and click **Record Administration**.
*   **Backend Technical Flow**:
    *   **Django Model**: `MedicationAdministration` (in `care/care/emr/models/medication_administration.py`)
    *   **Database Table**: `emr_medicationadministration`
    *   **Key Fields**: `request_id` (ForeignKey to `MedicationRequest`), `status="completed"`, `effective_datetime=current_time`.

### FLOW-26: Dispensing Medication (Pharmacy Workflow)
*   **Layperson UI Flow**:
    1.  The pharmacist opens the **Pending Prescriptions** queue.
    2.  Select the patient's order.
    3.  Enter quantity dispensed and click **Dispense**.
*   **Backend Technical Flow**:
    *   **Django Model**: `MedicationDispense` (in `care/care/emr/models/medication_dispense.py`)
    *   **Database Table**: `emr_medicationdispense`
    *   **Key Fields**: `request_id`, `status="completed"`, `quantity_dispensed`.

### FLOW-27: Recording Patient Allergy & Intolerance History
*   **Layperson UI Flow**:
    1.  On the patient profile, open the **Allergies & Intolerances** tab.
    2.  Click **Record Allergy**.
    3.  Select allergen substance (e.g. `Penicillin`), criticality (`High`), and type (`Allergy`).
    4.  Click **Save**.
*   **Backend Technical Flow**:
    *   **Django Model**: `AllergyIntolerance` (in `care/care/emr/models/allergy_intolerance.py`)
    *   **Database Table**: `emr_allergyintolerance`
    *   **Key Fields**: `patient_id`, `substance` (JSONField), `criticality="high"`, `status="active"`.

### FLOW-28: Logging Patient Consent Forms
*   **Layperson UI Flow**:
    1.  Before performing an invasive procedure, open the **Consents** panel on the patient profile.
    2.  Click **Add Consent**.
    3.  Select the procedure consent template, upload the signed document scan, and select the witness name.
    4.  Click **Record Consent**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Consent` (in `care/care/emr/models/consent.py`)
    *   **Database Table**: `emr_consent`
    *   **Key Fields**: `patient_id`, `encounter_id`, `status="active"`, `attachment_url`.

---

## 7. Domain G: Laboratory & Diagnostic Workflows

### FLOW-29: Doctor Ordering a Lab Test (Service Request)
*   **Layperson UI Flow**:
    1.  In the Encounter panel, click **Order Lab Test**.
    2.  Select test, e.g. `Complete Blood Count (CBC)`.
    3.  Select priority (`Urgent`, `Routine`) and enter instructions.
    4.  Click **Place Order**.
*   **Backend Technical Flow**:
    *   **Django Model**: `ServiceRequest` (in `care/care/emr/models/service_request.py`)
    *   **Database Table**: `emr_servicerequest`
    *   **Key Fields**: `patient_id`, `encounter_id`, `category="laboratory"`, `status="active"`.

### FLOW-30: Technician Collecting a Specimen Sample
*   **Layperson UI Flow**:
    1.  The Lab Technician opens the **Lab Queue** and clicks **Collect Specimen** next to the pending order.
    2.  Scan or enter barcode on sample tube (**Accession Identifier**).
    3.  Select specimen type (`Blood`, `Urine`) and confirm collection time.
    4.  Click **Register**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Specimen` (in `care/care/emr/models/specimen.py`)
    *   **Database Table**: `emr_specimen`
    *   **Key Fields**: `accession_identifier`, `status="collected"`, `specimen_type` JSONField, `service_request_id`.

### FLOW-31: Defining Custom Lab Tests & Specimen Guidelines
*   **Layperson UI Flow**:
    1.  Go to **Lab Management > Test Definitions** and click **Create Test Definition**.
    2.  Enter code, name (e.g. `Hemoglobin`), value type (e.g. `Numeric`), and default Reference Ranges.
    3.  Click **Save**.
*   **Backend Technical Flow**:
    *   **Django Model**: `ObservationDefinition` (in `care/care/emr/models/observation_definition.py`) & `SpecimenDefinition`
    *   **Database Tables**: `emr_observationdefinition`, `emr_specimendedefinition`.

### FLOW-32: Logging Lab Test Observations (Entering Results)
*   **Layperson UI Flow**:
    1.  Select the collected specimen in EMR and click **Enter Lab Results**.
    2.  Fill in the values (e.g. Hemoglobin: `13.5`).
    3.  Enter interpretation (e.g. `Normal`).
    4.  Click **Save Draft**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Observation` (in `care/care/emr/models/observation.py`)
    *   **Database Table**: `emr_observation`
    *   **Key Fields**: `value` (JSONField storing numerical values), `interpretation`, `specimen_id`.

### FLOW-33: Finalizing Diagnostic Reports
*   **Layperson UI Flow**:
    1.  In the draft results window, click **Finalize Lab Report**.
    2.  Write clinical conclusions and click **Submit**.
*   **Backend Technical Flow**:
    *   **Django Model**: `DiagnosticReport` (in `care/care/emr/models/diagnostic_report.py`)
    *   **Actions**:
        1. Creates `DiagnosticReport` row linking all patient observations.
        2. Sets `ServiceRequest.status = "completed"`.
        3. Updates `Observation.status = "final"`.

### FLOW-34: Setting up a Specialty Laboratory Department
*   **Layperson UI Flow**:
    1.  Navigate to your facility and go to **Locations**.
    2.  Click **Add Location** and name it `Clinical Pathology Lab` (Type: `Building` or `Room`).
    3.  Inside Pathology Lab, click **Add Location** to add sub-departments: `Haematology Room` and `Biochemistry Testing Block` (Type: `Room`, Parent: `Clinical Pathology Lab`).
*   **Backend Technical Flow**:
    *   Inserts in `emr_facilitylocation` creating nested spatial trees linked to parent identifiers.

### FLOW-35: Registering Lab Devices & Analyzers (Assets)
*   **Layperson UI Flow**:
    1.  Open `Haematology Room` inside locations.
    2.  Click **Add Device / Asset**.
    3.  Enter Name (e.g. `Automated Hematology Analyzer 01`), Model, and Serial Number.
    4.  Set status to `Active`.
    5.  Click **Save**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Device` (in `care/care/emr/models/device.py`)
    *   **Database Table**: `emr_device`
    *   **Key Fields**: `name`, `location_id` (points to `FacilityLocation`), `status`.

---

## 8. Domain H: Inventory & Asset Management

### FLOW-36: Registering an Asset in a Facility (e.g. Ventilator / Incubator)
*   **Layperson UI Flow**:
    1.  Go to **Assets / Inventory** inside a facility.
    2.  Click **Register Asset**.
    3.  Enter name (e.g., `ICU Ventilator #4`), type (`Clinical Asset`), location (e.g. `ICU Ward 2`), and status (`In Use`).
    4.  Click **Save**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Device` (re-used for hardware/assets in EMR).
    *   **Database Write**: Inserts record in `emr_device`.

### FLOW-37: Tracking Asset Maintenance & Downtime logs
*   **Layperson UI Flow**:
    1.  Open the Asset details page.
    2.  Click **Report Issue / Maintenance**.
    3.  Enter issue details, select status (`Downtime / Out of Order`), and save.
*   **Backend Technical Flow**:
    *   **Actions**:
        1. Updates `Device.status = "maintenance"`.
        2. Logs maintenance details under audit tables.

### FLOW-38: Creating a Stock Purchase Request (Care to Odoo ERP Sync)
*   **Layperson UI Flow**:
    1.  Navigate to **Inventory > Purchase Requests** in EMR.
    2.  Click **New Request**.
    3.  Select item (e.g. `Disposable Syringes 5ml`), enter quantity, and click **Submit**.
*   **Backend Technical Flow**:
    *   **Django Model**: `SupplyRequest` (in `care/care/emr/models/supply_request.py`)
    *   **Database Table**: `emr_supplyrequest`
    *   **Sync Logic**: Signal dispatches request details to Odoo ERP, automatically generating a Purchase Order Draft (`purchase.order`) inside Odoo.

### FLOW-39: Stock Entry (Receiving Inventory items)
*   **Layperson UI Flow**:
    1.  Open the inventory registry and click **Record Stock Intake**.
    2.  Select item (`Syringes`), batch number, expiry date, and quantity received.
    3.  Click **Save**.
*   **Backend Technical Flow**:
    *   **Django Model**: `InventoryItem` (in `care/care/emr/models/inventory_item.py`)
    *   **Database Table**: `emr_inventoryitem`
    *   **Key Fields**: `product_id`, `quantity`, `expiry_date`.

---

## 9. Domain I: Billing, Finance, Insurance, & ERP

### FLOW-40: Adding Charge Items & Services to an Encounter
*   **Layperson UI Flow**:
    1.  During an encounter, open the **Billing & Charges** tab.
    2.  Click **Add Charge Item**.
    3.  Select service (e.g. `ICU Bed Charge`, `CBC Lab Test Charge`) and enter quantity.
    4.  Click **Add**.
*   **Backend Technical Flow**:
    *   **Django Model**: `ChargeItem` (in `care/care/emr/models/charge_item.py`)
    *   **Database Table**: `emr_chargeitem`
    *   **Key Fields**: `encounter_id`, `quantity`, `price`, `charge_item_definition_id`.

### FLOW-41: Generating Patient Invoices
*   **Layperson UI Flow**:
    1.  Open the active Encounter dashboard and click **Generate Invoice**.
    2.  Review all registered charge items and totals.
    3.  Click **Finalize and Issue Invoice**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Invoice` (in `care/care/emr/models/invoice.py`)
    *   **Database Table**: `emr_invoice`
    *   **Actions**: Sets invoice status to `issued`, locks charge items.

### FLOW-42: Real-time Sync of Patient Invoices to Odoo ERP
*   **Layperson UI Flow**:
    *   *Automated Process*: No user action required. Once EMR issues the invoice, the backend signal automatically runs in the background.
*   **Backend Technical Flow**:
    *   **Trigger**: Django `post_save` signal on the `Invoice` model.
    *   **Connector Integration**: Dispatches API payload containing partner invoice data to the FastAPI connector.
    *   **Odoo Action**: Creates a customer invoice (`account.move`) in Odoo ERP, setting standard ledger accounts.

### FLOW-43: Syncing Payment Receipts & Transactions to Odoo Ledger
*   **Layperson UI Flow**:
    1.  In EMR, navigate to the patient's billing panel and click **Record Payment**.
    2.  Enter amount, payment mode (Cash, Card, UPI), and transaction ID.
    3.  Click **Confirm Payment**.
*   **Backend Technical Flow**:
    *   **Django Model**: `PaymentReconciliation` (in `care/care/emr/models/payment_reconciliation.py`)
    *   **Replication**: Backend signals transmit payment metadata to Odoo ERP, creating a matching payment receipt transaction record.

### FLOW-44: Odoo ERP Payment Reconciliation
*   **Layperson UI Flow**:
    1.  Log in to Odoo ERP UI and open the **Invoicing / Accounting** module.
    2.  Go to **Payments** and select the payment receipt.
    3.  Click **Reconcile** to link the payment receipt to the issued customer invoice (`account.move`).
*   **Backend Technical Flow**:
    *   **Odoo Action**: Performs Odoo ledger balancing, closing the open receivable account balance for the partner.

### FLOW-45: Processing Patient Insurance Details
*   **Layperson UI Flow**:
    1.  During registration or admission, open the patient's **Insurance** tab.
    2.  Click **Add Insurance Policy**.
    3.  Select the insurance provider company, policy/member number, and validity dates.
    4.  Click **Save**.
*   **Backend Technical Flow**:
    *   **Django Models**: `InsuranceClaim` and `InsuranceCompany` (replicated in Odoo accounting tables).

### FLOW-46: Submitting an Insurance Claim
*   **Layperson UI Flow**:
    1.  When patient is billed, click **Submit Insurance Claim** instead of direct invoicing.
    2.  Verify the claim code, diagnostic code (ICD-10), and requested coverage amount.
    3.  Click **Submit Claim**.
*   **Backend Technical Flow**:
    *   **Django Model**: `InsuranceClaim`
    *   **State Machine Action**: Sets status to `pending_claim`, locks billing items, and dispatches claims records to the Odoo ERP accounting ledger.

---

## 10. Domain J: Reporting & BI Analytics (Metabase)

Metabase accesses the PostgreSQL container directly. Administrative queries can audit operational flows in real-time.

### FLOW-47: Auditing District-wise Bed Occupancy (Metabase Dashboard)
*   **Metabase Query Logic**:
    1.  Open Metabase and click **Ask a Question > Native Query**.
    2.  Select **Care Database (Production)**.
    3.  Run the query:
        ```sql
        SELECT 
            o.name AS district_name,
            COUNT(l.id) AS total_beds,
            COUNT(l.current_encounter_id) AS occupied_beds
        FROM emr_facilitylocation l
        JOIN facility_facility f ON f.id = l.facility_id
        JOIN emr_organization o ON o.id = f.geo_organization_id
        WHERE l.status = 'active'
        GROUP BY o.name;
        ```
    4.  Visualize as a Bar Chart.

### FLOW-48: Tracking EMR-to-Odoo Invoice Sync Discrepancies
*   **Metabase Query Logic**:
    1.  Create a native SQL query in Metabase:
        ```sql
        SELECT 
            ei.id AS emr_invoice_id,
            ei.amount AS emr_amount,
            am.id AS odoo_invoice_id,
            am.amount_total AS odoo_amount
        FROM emr_invoice ei
        LEFT JOIN account_move am ON am.ref = CAST(ei.id AS VARCHAR)
        WHERE am.id IS NULL OR ei.amount != am.amount_total;
        ```
    2.  Configure alert notifications if this query returns rows, indicating a sync discrepancy.
