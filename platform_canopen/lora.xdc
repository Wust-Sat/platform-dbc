<?xml version="1.0" encoding="UTF-8"?>
<ISO15745Profile xmlns="http://www.profibus.com/GSDML/2003/11/DeviceProfile" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.profibus.com/GSDML/2003/11/DeviceProfile ..\xsd\ISO15745Profile.xsd">
  <ProfileHeader>
    <ProfileIdentification>WUST-Sat LoRa Module CANopen Definition</ProfileIdentification>
    <ProfileRevision>1.0</ProfileRevision>
    <ProfileName>WUST-Sat LoRa</ProfileName>
    <ProfileSource>WUST</ProfileSource>
    <ProfileClassID>Device</ProfileClassID>
    <ISO15745Reference>
      <ISO15745Part>4</ISO15745Part>
      <ISO15745Edition>1</ISO15745Edition>
      <ProfileTechnology>CANopen</ProfileTechnology>
    </ISO15745Reference>
  </ProfileHeader>
  <ProfileBody DeviceType="CANopen" ProfileType="Device" xsi:type="ProfileBody_Device_CANopen">
    <!-- Device Identity -->
    <DeviceIdentity VendorID="0x00000057" VendorName="WUST" ProductCode="0x00000004" ProductName="WUST-Sat LoRa Module" RevisionNumber="0x00010000" OrderNumber="WUST-LORA-V1"/>
    <!-- Mandatory Objects -->
    <ApplicationObjectList>
      <ApplicationObject Index="1000" SubIndex="0" Name="Device Type" ObjectType="7" DataType="0007" AccessType="ro" DefaultValue="0x00000000"/>
      <ApplicationObject Index="1001" SubIndex="0" Name="Error Register" ObjectType="7" DataType="0005" AccessType="ro" DefaultValue="0x00"/>
      <ApplicationObject Index="1017" SubIndex="0" Name="Producer Heartbeat Time" ObjectType="7" DataType="0006" AccessType="rw" DefaultValue="1000"/> <!-- Default 1000 ms -->
      <ApplicationObject Index="1018" Name="Identity Object" ObjectType="9">
        <SubObject SubIndex="0" Name="Number of Entries" ObjectType="7" DataType="0005" AccessType="ro" DefaultValue="4"/>
        <SubObject SubIndex="1" Name="Vendor ID" ObjectType="7" DataType="0007" AccessType="ro" DefaultValue="0x00000057"/> <!-- Placeholder WUST ID -->
        <SubObject SubIndex="2" Name="Product Code" ObjectType="7" DataType="0007" AccessType="ro" DefaultValue="0x00000004"/> <!-- Based on HW ID -->
        <SubObject SubIndex="3" Name="Revision Number" ObjectType="7" DataType="0007" AccessType="ro" DefaultValue="0x00010000"/> <!-- v1.0 -->
        <SubObject SubIndex="4" Name="Serial Number" ObjectType="7" DataType="0007" AccessType="ro" DefaultValue="0x00000001"/> <!-- Placeholder SN -->
      </ApplicationObject>
      <!-- Manufacturer Specific Objects for Testing -->
      <ApplicationObject Index="2000" SubIndex="0" Name="LoRa Control Register" ObjectType="7" DataType="0005" AccessType="rw" DefaultValue="0"/> <!-- Simple writable byte -->
    </ApplicationObjectList>
    <!-- PDO/SDO/NMT etc. configuration would go here in a full XDC, omitted for minimal example -->
  </ProfileBody>
</ISO15745Profile>
