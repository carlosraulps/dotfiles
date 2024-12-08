# Configuración del Lector de Huellas en Linux

Este documento describe los pasos realizados para configurar y activar correctamente el lector de huellas dactilares en un ThinkPad T460 con Arch Linux.

---

## **Requisitos**

1. **Paquetes necesarios**:
   - `fprintd`: Demonio para manejar huellas dactilares.
   - `libfprint`: Librería para interactuar con lectores de huellas.
   - `polkit`: Manejo de políticas de autenticación.

   Comando para instalarlos:
   ```bash
   sudo pacman -S fprintd libfprint polkit
   ```

---

## **Pasos de Configuración**

### 1. Verificar el Lector de Huellas
Utilizamos `lsusb` para identificar el lector conectado:
```bash
lsusb
```
Resultado esperado:
```plaintext
Bus 001 Device 005: ID 138a:0017 Validity Sensors, Inc. VFS 5011 fingerprint sensor
```

---

### 2. Configurar Permisos de Acceso

#### a) Reglas de `udev`
Creamos una regla para asignar permisos al dispositivo:
```bash
sudo nvim /etc/udev/rules.d/99-fingerprint.rules
```

Contenido:
```plaintext
ATTRS{idVendor}=="138a", ATTRS{idProduct}=="0017", MODE="0660", GROUP="wheel""
```

Recargamos las reglas:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

#### b) Verificar Permisos
Asegúrate de que los permisos del dispositivo sean correctos:
```bash
ls -l /dev/bus/usb/001/005
```
Resultado esperado:
```plaintext
crw-rw---- 1 root ...
```

---

### 3. Configurar PolicyKit
Creamos una regla de PolicyKit para permitir a los usuarios del grupo `input` usar el lector:
```bash
sudo nano /etc/polkit-1/rules.d/90-fprintd.rules
```

Contenido:
```javascript
polkit.addRule(function(action, subject) {
    if ((action.id == "net.reactivated.fprint.device.enroll" ||
         action.id == "net.reactivated.fprint.device.verify") &&
        subject.isInGroup("input")) {
        return polkit.Result.YES;
    }
});
```

Reiniciamos el servicio de PolicyKit:
```bash
sudo systemctl restart polkit
```

---

### 4. Registrar la Huella
Usamos el siguiente comando para registrar una huella:
```bash
fprintd-enroll
```
El sistema te pedirá que coloques tu dedo varias veces hasta completar el registro.

---

### 5. Configurar PAM para la Autenticación
Editamos los archivos de configuración de PAM para permitir el uso de huellas:

#### a) Para `sudo`:
```bash
sudo nano /etc/pam.d/sudo
```
Agregamos:
```plaintext
auth sufficient pam_fprintd.so
auth required pam_unix.so
```

#### b) Para el login gráfico (opcional):
Si usas GDM o SDDM:
```bash
sudo nano /etc/pam.d/gdm-password
```
O para SDDM:
```bash
sudo nano /etc/pam.d/sddm
```
Agregamos:
```plaintext
auth sufficient pam_fprintd.so
```

---

### 6. Probar la Configuración
- Probar `sudo`:
  ```bash
  sudo ls
  ```
  Debería solicitar la huella y, como alternativa, aceptar la contraseña.

- Registrar un nuevo usuario:
  ```bash
  fprintd-enroll
  ```

---

## **Verificación de Logs**
Si algo no funciona correctamente, revisa los logs de `fprintd`:
```bash
journalctl -u fprintd
```

---

## **Archivos de Configuración Modificados**

1. `/etc/pam.d/sudo`
2. `/etc/pam.d/system-auth`
3. `/etc/udev/rules.d/99-fingerprint.rules`
4. `/etc/polkit-1/rules.d/90-fprintd.rules`

---

## **Conclusión**
Este proceso habilita correctamente el lector de huellas en Arch Linux, permitiendo su uso tanto para `sudo` como para inicio de sesión gráfico. Si encuentras problemas adicionales, revisa los permisos de tu dispositivo o los servicios configurados.


