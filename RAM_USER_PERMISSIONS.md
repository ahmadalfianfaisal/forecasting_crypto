# Panduan Manajemen RAM User untuk Deploy ke Alibaba Cloud

## Hak Akses yang Dibutuhkan

Untuk bisa melakukan deployment ke Alibaba Cloud ECS, RAM user Anda harus memiliki hak akses berikut:

### 1. Hak Akses ECS Dasar
Policy yang dibutuhkan:
```
{
  "Version": "1",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:Describe*",
        "ecs:CreateInstance",
        "ecs:DeleteInstance",
        "ecs:StartInstance",
        "ecs:StopInstance",
        "ecs:RebootInstance",
        "ecs:ModifyInstanceAttribute"
      ],
      "Resource": "*"
    }
  ]
}
```

### 2. Hak Akses VPC
```
{
  "Version": "1",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "vpc:Describe*",
        "vpc:CreateVpc",
        "vpc:DeleteVpc"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3. Hak Akses Security Group
```
{
  "Version": "1",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:DescribeSecurityGroups",
        "ecs:AuthorizeSecurityGroup",
        "ecs:RevokeSecurityGroup"
      ],
      "Resource": "*"
    }
  ]
}
```

## Jika Anda Adalah Administrator RAM

Jika Anda memiliki akses administrator RAM, berikut cara memberikan izin ke user:

### 1. Login ke RAM Console
1. Buka: https://ram.console.aliyun.com/manage/overview
2. Login sebagai administrator

### 2. Buat Custom Policy
1. Klik "Policies" di menu kiri
2. Klik "Create Policy"
3. Beri nama policy (misal: "ECS-Deployment-Policy")
4. Masukkan policy document seperti di atas
5. Klik "OK"

### 3. Assign Policy ke User
1. Klik "Users" di menu kiri
2. Pilih user yang akan diberi izin
3. Klik "Attach Policy"
4. Pilih policy yang telah dibuat
5. Klik "OK"

## Jika Anda Bukan Administrator

Jika Anda bukan administrator RAM, Anda perlu meminta izin berikut ke administrator:

### Email Template untuk Permintaan Izin

---
Subject: Permintaan Izin RAM untuk Deployment Aplikasi ke Alibaba Cloud ECS

Kepada Tim Administrasi RAM,

Saya membutuhkan izin untuk melakukan deployment aplikasi ke Alibaba Cloud ECS. Mohon diberikan hak akses berikut:

1. ECS Full Access atau setidaknya:
   - ecs:DescribeInstances
   - ecs:CreateInstance
   - ecs:DeleteInstance
   - ecs:StartInstance
   - ecs:StopInstance
   - ecs:RebootInstance

2. VPC Access:
   - vpc:DescribeVpcs
   - vpc:DescribeVSwitches

3. Security Group Access:
   - ecs:DescribeSecurityGroups
   - ecs:AuthorizeSecurityGroup

Akses ini diperlukan untuk:
- Membuat instance ECS untuk hosting aplikasi
- Mengkonfigurasi jaringan dan keamanan
- Mengelola lifecycle instance (start/stop)

Terima kasih atas bantuannya.

Hormat saya,
[Nama Anda]
---

## Verifikasi Izin

Setelah administrator memberikan izin, verifikasi dengan:

1. Login ke Alibaba Cloud Console
2. Coba akses halaman ECS
3. Coba buat instance kecil untuk testing

## Best Practices Keamanan

### 1. Principle of Least Privilege
- Berikan hanya izin yang diperlukan
- Hindari memberikan full admin access

### 2. Gunakan Access Key dengan Bijak
- Jangan hardcode access key di kode
- Gunakan environment variables
- Rotasi access key secara berkala

### 3. Monitor Aktivitas
- Aktifkan ActionTrail untuk logging aktivitas
- Periksa secara berkala aktivitas mencurigakan

## Troubleshooting Izin

### Error Umum dan Solusinya

1. **"Access Denied" saat membuat instance**
   - Cek apakah policy ECS sudah diattach ke user
   - Pastikan region yang dipilih sesuai

2. **Tidak bisa mengakses halaman ECS**
   - Pastikan RAM user memiliki izin dasar ECS
   - Coba login dengan akun root untuk konfirmasi

3. **Tidak bisa mengkonfigurasi security group**
   - Pastikan ada izin ECS untuk security group
   - Cek apakah security group sudah dibuat

## Alternatif Jika Tidak Bisa Mendapatkan Izin ECS

Jika Anda tidak bisa mendapatkan izin ECS, pertimbangkan alternatif berikut:

1. **Function Compute (FC)**
   - Serverless computing
   - Tidak perlu mengelola instance
   - Lebih hemat biaya untuk aplikasi kecil

2. **Container Service for Kubernetes (ACK)**
   - Jika aplikasi Anda bisa di-containerisasi
   - Lebih fleksibel untuk deployment

3. **Simple Application Server**
   - Opsi yang lebih sederhana
   - Cocok untuk aplikasi kecil

4. **Deploy ke Platform Lain**
   - Heroku
   - Render
   - Railway
   - AWS/GCP jika memiliki akses

---

Catatan:
- Selalu komunikasikan kebutuhan izin dengan tim administrasi
- Ikuti kebijakan keamanan perusahaan
- Gunakan akun pribadi untuk testing jika diperlukan