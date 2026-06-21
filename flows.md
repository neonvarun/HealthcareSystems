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
    3.  Enter `Kerala` as the **Name**.
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
    2.  Enter the name, e.g., `Ernakulam`.
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
    2.  Enter the name, e.g., `Kochi Corporation`.
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

### FLOW-05: Linking Geographic Governance boundaries to Facilities
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
    2.  Enter Name (e.g. `Govt Virology Lab Kochi`).
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

### FLOW-10: Registering Beds under a Room (Microbiology / Clinical Beds)
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

## 4. Domain D: Clinical Patient Workflows

### FLOW-15: Patient Registration
*   **Layperson UI Flow**:
    1.  Go to `/patient` and click **Register Patient**.
    2.  Input demographic fields (Name, Gender, DOB, Phone, Address, ID Proof).
    3.  Click **Submit**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Patient` (in `care/care/emr/models/patient.py`)
    *   **Database Table**: `emr_patient`
    *   **Key Fields**: `name`, `gender`, `date_of_birth`, `phone_number`.

### FLOW-16: Creating a Patient Encounter (Admission / Consultation)
*   **Layperson UI Flow**:
    1.  Open the Patient profile and click **Create Encounter**.
    2.  Select **Encounter Type**: `Inpatient / Admission` or `Outpatient / Consultation`.
    3.  Select the **Admitting Doctor** and Facility.
    4.  Click **Confirm**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Encounter` (in `care/care/emr/models/encounter.py`)
    *   **Database Table**: `emr_encounter`
    *   **Key Fields**: `patient_id`, `status="active"`, `class` (e.g. inpatient), `facility_id`.

### FLOW-17: Assigning a Patient to a Bed (Encounter Location Association)
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

### FLOW-18: Transferring a Patient to a Different Bed / Room
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

### FLOW-19: Recording Clinical Vitals & Daily Rounds
*   **Layperson UI Flow**:
    1.  On the active patient profile, click **Log Vitals / Daily Round**.
    2.  Enter Pulse, Blood Pressure, Respiratory Rate, Temperature, and Consciousness Level.
    3.  Click **Save**.
*   **Backend Technical Flow**:
    *   **Django Model**: `DailyRound` (in `care/care/facility/models/patient.py`)
    *   **Key Fields**: `bp`, `pulse`, `temperature`, `consciousness_level`.

### FLOW-20: Discharging a Patient & Vacating Locations
*   **Layperson UI Flow**:
    1.  Open the active Encounter dashboard and click **Discharge Patient**.
    2.  Select discharge status (e.g., Recovered), enter notes, and confirm.
*   **Backend Technical Flow**:
    *   **Actions**:
        1. Set `Encounter.status = "completed"`.
        2. Set `FacilityLocationEncounter.end_datetime = discharge_time`.
        3. Set `FacilityLocation.current_encounter_id = NULL` (releases the bed).

---

## 5. Domain E: Laboratory & Diagnostic Workflows

### FLOW-21: Doctor Ordering a Lab Test (Service Request)
*   **Layperson UI Flow**:
    1.  In the Encounter panel, click **Order Lab Test**.
    2.  Select test, e.g. `Complete Blood Count (CBC)`.
    3.  Select priority (`Urgent`, `Routine`) and enter instructions.
    4.  Click **Place Order**.
*   **Backend Technical Flow**:
    *   **Django Model**: `ServiceRequest` (in `care/care/emr/models/service_request.py`)
    *   **Database Table**: `emr_servicerequest`
    *   **Key Fields**: `patient_id`, `encounter_id`, `category="laboratory"`, `status="active"`.

### FLOW-22: Technician Collecting a Specimen Sample
*   **Layperson UI Flow**:
    1.  The Lab Technician opens the **Lab Queue** and clicks **Collect Specimen** next to the pending order.
    2.  Scan or enter barcode barcode on sample tube (**Accession Identifier**).
    3.  Select specimen type (`Blood`, `Urine`) and confirm collection time.
    4.  Click **Register**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Specimen` (in `care/care/emr/models/specimen.py`)
    *   **Database Table**: `emr_specimen`
    *   **Key Fields**: `accession_identifier`, `status="collected"`, `specimen_type` JSONField, `service_request_id`.

### FLOW-23: Defining Custom Lab Tests & Specimen Guidelines
*   **Layperson UI Flow**:
    1.  Go to **Lab Management > Test Definitions** and click **Create Test Definition**.
    2.  Enter code, name (e.g. `Hemoglobin`), value type (e.g. `Numeric`), and default Reference Ranges.
    3.  Click **Save**.
*   **Backend Technical Flow**:
    *   **Django Model**: `ObservationDefinition` (in `care/care/emr/models/observation_definition.py`) & `SpecimenDefinition`
    *   **Database Tables**: `emr_observationdefinition`, `emr_specimendedefinition`.

### FLOW-24: Logging Lab Test Observations (Entering Results)
*   **Layperson UI Flow**:
    1.  Select the collected specimen in EMR and click **Enter Lab Results**.
    2.  Fill in the values (e.g. Hemoglobin: `13.5`).
    3.  Enter interpretation (e.g. `Normal`).
    4.  Click **Save Draft**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Observation` (in `care/care/emr/models/observation.py`)
    *   **Database Table**: `emr_observation`
    *   **Key Fields**: `value` (JSONField storing numerical values), `interpretation`, `specimen_id`.

### FLOW-25: Finalizing Diagnostic Reports
*   **Layperson UI Flow**:
    1.  In the draft results window, click **Finalize Lab Report**.
    2.  Write clinical conclusions and click **Submit**.
*   **Backend Technical Flow**:
    *   **Django Model**: `DiagnosticReport` (in `care/care/emr/models/diagnostic_report.py`)
    *   **Actions**:
        1. Creates `DiagnosticReport` row linking all patient observations.
        2. Sets `ServiceRequest.status = "completed"`.
        3. Updates `Observation.status = "final"`.

---

## 6. Domain F: Billing, ERP, & Accounting Flows

### FLOW-26: Adding Charge Items & Services to an Encounter
*   **Layperson UI Flow**:
    1.  During an encounter, open the **Billing & Charges** tab.
    2.  Click **Add Charge Item**.
    3.  Select service (e.g. `ICU Bed Charge`, `CBC Lab Test Charge`) and enter quantity.
    4.  Click **Add**.
*   **Backend Technical Flow**:
    *   **Django Model**: `ChargeItem` (in `care/care/emr/models/charge_item.py`)
    *   **Database Table**: `emr_chargeitem`
    *   **Key Fields**: `encounter_id`, `quantity`, `price`, `charge_item_definition_id`.

### FLOW-27: Generating Patient Invoices
*   **Layperson UI Flow**:
    1.  Open the active Encounter dashboard and click **Generate Invoice**.
    2.  Review all registered charge items and totals.
    3.  Click **Finalize and Issue Invoice**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Invoice` (in `care/care/emr/models/invoice.py`)
    *   **Database Table**: `emr_invoice`
    *   **Actions**: Sets invoice status to `issued`, locks charge items.

### FLOW-28: Real-time Sync of Patient Invoices to Odoo ERP
*   **Layperson UI Flow**:
    *   *Automated Process*: No user action required. Once EMR issues the invoice, the backend signal automatically runs in the background.
*   **Backend Technical Flow**:
    *   **Trigger**: Django `post_save` signal on the `Invoice` model.
    *   **Connector Integration**: Dispatches API payload containing partner invoice data to the FastAPI connector.
    *   **Odoo Action**: Creates a customer invoice (`account.move`) in Odoo ERP, setting standard ledger accounts.

### FLOW-29: Syncing Payment Receipts & Transactions to Odoo Ledger
*   **Layperson UI Flow**:
    1.  In EMR, navigate to the patient's billing panel and click **Record Payment**.
    2.  Enter amount, payment mode (Cash, Card, UPI), and transaction ID.
    3.  Click **Confirm Payment**.
*   **Backend Technical Flow**:
    *   **Django Model**: `PaymentReconciliation` (in `care/care/emr/models/payment_reconciliation.py`)
    *   **Replication**: Backend signals transmit payment metadata to Odoo ERP, creating a matching payment receipt transaction record.

### FLOW-30: Odoo ERP Payment Reconciliation & Financial Closing
*   **Layperson UI Flow**:
    1.  Log in to Odoo ERP UI and open the **Invoicing / Accounting** module.
    2.  Go to **Payments** and select the payment receipt.
    3.  Click **Reconcile** to link the payment receipt to the issued customer invoice (`account.move`).
*   **Backend Technical Flow**:
    *   **Odoo Action**: Performs Odoo ledger balancing, closing the open receivable account balance for the partner.

---

## 7. Domain G: Advanced Lab & Location Scenarios (Microbiology Lab Process)

Setting up and operating a specialized **Microbiology Lab** requires a combination of several governance, spatial, and lab workflows.

### FLOW-31: Registering a Microbiology Lab Facility
*   **Layperson UI Flow**:
    1.  Go to **Facilities** and click **Create Facility**.
    2.  Name it `Govt Microbiology & Virology Research Center`.
    3.  Select **Facility Type** as `Govt Labs`.
    4.  Click **Create**.
*   **Backend Technical Flow**:
    *   Writes to `facility_facility` with `facility_type=9`.

### FLOW-32: Adding Lab Departments (Locations)
*   **Layperson UI Flow**:
    1.  Navigate to the Virology Center and click the **Locations** tab.
    2.  Add a location named `Virology Block` (Type: `Building`).
    3.  Add child location named `Bacteriology Laboratory` (Type: `Room`, Parent: `Virology Block`).
    4.  Add child location named `Mycology Testing Area` (Type: `Room`, Parent: `Virology Block`).
*   **Backend Technical Flow**:
    *   Creates hierarchical `FacilityLocation` records with parent pointers (`parent_id`).

### FLOW-33: Adding Specialized Lab Devices / Assets
*   **Layperson UI Flow**:
    1.  In the Locations panel, select `Bacteriology Laboratory`.
    2.  Click **Register Asset / Device**.
    3.  Enter name (e.g. `Automated Blood Culture Incubator 01` or `RT-PCR Thermal Cycler`).
    4.  Set status to `Active`.
    5.  Click **Save**.
*   **Backend Technical Flow**:
    *   **Django Model**: `Device` (in `care/care/emr/models/device.py`)
    *   **Database Table**: `emr_device`
    *   **Key Fields**: `name`, `location_id`, `status`.

### FLOW-34: Defining Microbiological Cultures & Gram Stain Tests
*   **Layperson UI Flow**:
    1.  Navigate to **Lab Management > Test Definitions** and click **Create Test Definition**.
    2.  Name it `Blood Culture & Sensitivity (C&S)`.
    3.  Add specific component observations (e.g., `Gram Stain Result`, `Organism Identified`, `Antibiotic Sensitivity Profile`).
    4.  Select specimen definition requirements (e.g., `Whole Blood` sample in standard Culture Bottle).
    5.  Click **Save**.
*   **Backend Technical Flow**:
    *   Creates an `ObservationDefinition` container with child component schema layouts.

### FLOW-35: Requesting, Collecting, and Processing Microbiology Cultures
*   **Layperson UI Flow**:
    1.  A doctor orders `Blood Culture & Sensitivity` for a patient.
    2.  The lab tech draws blood, enters a barcode accession number (e.g., `MC-98765`), and clicks **Register Specimen**.
    3.  When growth is detected, the technician inputs observations:
        *   *Gram Stain*: `Gram-Negative Bacilli`
        *   *Organism*: `Escherichia coli`
        *   *Sensitivity*: `Amikacin (Sensitive)`, `Ampicillin (Resistant)`.
    4.  The technician clicks **Finalize Diagnostic Report** to complete the microbiology lab loop.
*   **Backend Technical Flow**:
    *   Creates a `ServiceRequest` (order) ➔ `Specimen` (Accession MC-98765) ➔ multiple `Observation` entries for Gram stain, Organism, and Antibiotic sensitivity matrices, grouped under a `DiagnosticReport`.
