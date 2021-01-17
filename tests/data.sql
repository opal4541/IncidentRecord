USE [IncidentRecord]
GO
SET IDENTITY_INSERT [dbo].[User] ON 

INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType]) VALUES (1, N'Opal', N'6010017', N'Nuntanuch', N'Tharapong', N'Admin')
INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType]) VALUES (2, N'Pim', N'6013633', N'Kamonrut', N'Vorrawongprasert', N'Admin')
INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType]) VALUES (3, N'Nueng', N'1234567', N'Chayapol', N'Moemeng', N'User')
SET IDENTITY_INSERT [dbo].[User] OFF
GO
SET IDENTITY_INSERT [dbo].[Customer] ON 

INSERT [dbo].[Customer] ([CustomerID], [FirstName], [LastName], [Phone]) VALUES (1, N'Grid', N'Kornsutatipkul', N'0943504350')
INSERT [dbo].[Customer] ([CustomerID], [FirstName], [LastName], [Phone]) VALUES (2, N'Shiv', N'Dechasakphan', NULL)
SET IDENTITY_INSERT [dbo].[Customer] OFF
GO
SET IDENTITY_INSERT [dbo].[Car] ON 

INSERT [dbo].[Car] ([CarID], [CustomerID], [LicensePlate]) VALUES (1, 1, N'2ตก4990')
INSERT [dbo].[Car] ([CarID], [CustomerID], [LicensePlate]) VALUES (2, 2, N'2กต29')
SET IDENTITY_INSERT [dbo].[Car] OFF
GO
SET IDENTITY_INSERT [dbo].[Incident] ON 

INSERT [dbo].[Incident] ([IncidentID], [CarID], [UserID], [Description], [Type], [StartTimestamp], [EndTimestamp], [Status]) VALUES (1, 1, 2, N'ไม่จ่ายค่าน้ำมัน', N'Red', CAST(N'2021-01-17T10:00:00.000' AS DateTime), NULL, N'Active')
INSERT [dbo].[Incident] ([IncidentID], [CarID], [UserID], [Description], [Type], [StartTimestamp], [EndTimestamp], [Status]) VALUES (2, 2, 1, N'บัตรเครดิตมีปัญหา', N'Yellow', CAST(N'2021-01-18T10:30:00.000' AS DateTime), NULL, N'Inactive')
SET IDENTITY_INSERT [dbo].[Incident] OFF
GO
SET IDENTITY_INSERT [dbo].[History] ON 

INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (1, 1, CAST(N'2021-01-17T19:40:10.000' AS DateTime), NULL, NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (2, 2, CAST(N'2021-01-18T09:01:22.000' AS DateTime), NULL, NULL)
SET IDENTITY_INSERT [dbo].[History] OFF
GO
