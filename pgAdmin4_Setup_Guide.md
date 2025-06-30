# 🐘 pgAdmin 4 Setup Guide for SkillSnap

## Step 1: Connect to PostgreSQL Server

1. **Open pgAdmin 4**
2. **Right-click "Servers"** in the left panel
3. **Select "Create" → "Server"**

### Connection Details:
- **General Tab:**
  - Name: `SkillSnap Local`
  - Server group: `Servers`

- **Connection Tab:**
  - Host name/address: `localhost`
  - Port: `5432`
  - Maintenance database: `postgres`
  - Username: `postgres` (or your PostgreSQL superuser)
  - Password: (your PostgreSQL password)

4. **Click "Save"**

## Step 2: Create SkillSnap Database

1. **Connect to your PostgreSQL server** in pgAdmin 4
2. **Right-click on the server** → "Query Tool"
3. **Copy and paste** the contents of `setup_database.sql`
4. **Click "Execute"** (F5)

Or manually:
1. **Right-click "Databases"** → "Create" → "Database"
2. **Name:** `skillsnap`
3. **Owner:** `postgres`
4. **Click "Save"**

## Step 3: Create SkillSnap User

1. **Right-click "Login/Group Roles"** → "Create" → "Login/Group Role"
2. **General Tab:**
   - Name: `skillsnap_user`
3. **Definition Tab:**
   - Password: `skillsnap_password`
4. **Privileges Tab:**
   - ✅ Can login?
   - ✅ Create databases?
5. **Click "Save"**

## Step 4: Connect to SkillSnap Database

1. **Right-click "Servers"** → "Create" → "Server"
2. **General Tab:**
   - Name: `SkillSnap Database`
3. **Connection Tab:**
   - Host: `localhost`
   - Port: `5432`
   - Database: `skillsnap`
   - Username: `skillsnap_user`
   - Password: `skillsnap_password`
4. **Click "Save"**

## Step 5: View SkillSnap Data

Once your backend is running, you'll see these tables in pgAdmin 4:

### 📊 **SkillSnap Tables:**
- **candidates** - Candidate profiles and information
- **recruiters** - Recruiter accounts and companies  
- **challenges** - Voice challenge templates
- **challenge_submissions** - Candidate responses and scores
- **voice_analytics** - Voice quality analysis data
- **api_usage** - API usage tracking

### 🔍 **Viewing Data:**
1. **Expand** `SkillSnap Database` → `Databases` → `skillsnap` → `Schemas` → `public` → `Tables`
2. **Right-click any table** → "View/Edit Data" → "All Rows"
3. **View candidate registrations, voice recordings, and AI scores!**

### 📝 **Running Queries:**
```sql
-- View all candidates
SELECT * FROM candidates;

-- View challenge submissions with scores
SELECT 
    c.full_name,
    ch.role,
    cs.overall_score,
    cs.transcription,
    cs.submission_status
FROM candidates c
JOIN challenge_submissions cs ON c.id = cs.candidate_id
JOIN challenges ch ON cs.challenge_id = ch.id
ORDER BY cs.created_at DESC;

-- View top scoring candidates
SELECT 
    c.full_name,
    c.role_interest,
    AVG(cs.overall_score) as avg_score
FROM candidates c
JOIN challenge_submissions cs ON c.id = cs.candidate_id
WHERE cs.overall_score IS NOT NULL
GROUP BY c.id, c.full_name, c.role_interest
ORDER BY avg_score DESC;
```

## 🎯 **What You Can Monitor:**

✅ **Candidate Registrations** - See who signs up  
✅ **Voice Recordings** - Track submission status  
✅ **AI Scoring Results** - View detailed analysis  
✅ **Recruiter Activity** - Monitor usage  
✅ **Challenge Performance** - Analytics by role  

## 🔧 **Troubleshooting:**

**Connection Failed?**
- Check PostgreSQL is running
- Verify port 5432 is open
- Confirm username/password

**Tables Not Visible?**
- Start your SkillSnap backend server
- Tables are created automatically

**Permission Denied?**
- Re-run the privileges commands from `setup_database.sql`

---

🎉 **Your SkillSnap database is now ready for pgAdmin 4 management!** 