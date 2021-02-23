USE [IncidentRecord]
GO
SET IDENTITY_INSERT [dbo].[Car] ON 

INSERT [dbo].[Car] ([CarID], [LicensePlate]) VALUES (3, N'1กช361')
INSERT [dbo].[Car] ([CarID], [LicensePlate]) VALUES (10, N'2กต29')
INSERT [dbo].[Car] ([CarID], [LicensePlate]) VALUES (1, N'5กศ8444')
INSERT [dbo].[Car] ([CarID], [LicensePlate]) VALUES (9, N'6กข3633')
INSERT [dbo].[Car] ([CarID], [LicensePlate]) VALUES (7, N'6กฎ8199')
INSERT [dbo].[Car] ([CarID], [LicensePlate]) VALUES (2, N'8กฎ4574')
INSERT [dbo].[Car] ([CarID], [LicensePlate]) VALUES (6, N'8กร5437')
INSERT [dbo].[Car] ([CarID], [LicensePlate]) VALUES (8, N'8กอ8160')
INSERT [dbo].[Car] ([CarID], [LicensePlate]) VALUES (5, N'9กท6775')
INSERT [dbo].[Car] ([CarID], [LicensePlate]) VALUES (4, N'ขอ5025')
INSERT [dbo].[Car] ([CarID], [LicensePlate]) VALUES (11, N'ยน1578')
SET IDENTITY_INSERT [dbo].[Car] OFF
GO
SET IDENTITY_INSERT [dbo].[Customer] ON 

INSERT [dbo].[Customer] ([CustomerID], [CarID], [FirstName], [LastName], [Phone]) VALUES (1, 1, N'สมทรง', N'ลงบันได', NULL)
INSERT [dbo].[Customer] ([CustomerID], [CarID], [FirstName], [LastName], [Phone]) VALUES (2, 2, N'สมหมาย', N'หมายโมยของ', N'0811498765')
INSERT [dbo].[Customer] ([CustomerID], [CarID], [FirstName], [LastName], [Phone]) VALUES (3, 3, N'สมควร', N'นอนน้อย', N'0611498765')
INSERT [dbo].[Customer] ([CustomerID], [CarID], [FirstName], [LastName], [Phone]) VALUES (4, 4, N'', NULL, NULL)
INSERT [dbo].[Customer] ([CustomerID], [CarID], [FirstName], [LastName], [Phone]) VALUES (5, 5, N'โอโล่', N'โจ้โจ้', N'0848251841')
INSERT [dbo].[Customer] ([CustomerID], [CarID], [FirstName], [LastName], [Phone]) VALUES (6, 6, N'', NULL, NULL)
INSERT [dbo].[Customer] ([CustomerID], [CarID], [FirstName], [LastName], [Phone]) VALUES (7, 7, N'', NULL, NULL)
INSERT [dbo].[Customer] ([CustomerID], [CarID], [FirstName], [LastName], [Phone]) VALUES (8, 8, N'', NULL, NULL)
INSERT [dbo].[Customer] ([CustomerID], [CarID], [FirstName], [LastName], [Phone]) VALUES (9, 9, N'', NULL, NULL)
INSERT [dbo].[Customer] ([CustomerID], [CarID], [FirstName], [LastName], [Phone]) VALUES (10, 10, N'', NULL, NULL)
INSERT [dbo].[Customer] ([CustomerID], [CarID], [FirstName], [LastName], [Phone]) VALUES (11, 11, N'สมพร', NULL, NULL)
SET IDENTITY_INSERT [dbo].[Customer] OFF
GO
SET IDENTITY_INSERT [dbo].[History] ON 

INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (1, 1, CAST(N'2021-02-23T07:38:25.000' AS DateTime), CAST(N'2021-02-23T07:38:26.000' AS DateTime), N'เติม 95')
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (2, 2, CAST(N'2021-02-23T07:38:42.000' AS DateTime), CAST(N'2021-02-23T07:38:43.000' AS DateTime), NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (3, 3, CAST(N'2021-02-23T07:40:57.000' AS DateTime), NULL, NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (4, 1, CAST(N'2021-02-23T07:47:08.000' AS DateTime), CAST(N'2021-02-23T07:47:14.000' AS DateTime), NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (5, 2, CAST(N'2021-02-23T07:47:25.000' AS DateTime), CAST(N'2021-02-23T07:47:31.000' AS DateTime), NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (6, 3, CAST(N'2021-02-23T07:49:39.000' AS DateTime), CAST(N'2021-02-23T07:49:43.000' AS DateTime), NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (7, 4, CAST(N'2021-02-23T08:03:59.000' AS DateTime), CAST(N'2021-02-23T08:10:07.000' AS DateTime), NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (8, 5, CAST(N'2021-02-23T08:04:52.000' AS DateTime), NULL, NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (9, 6, CAST(N'2021-02-23T08:07:40.000' AS DateTime), CAST(N'2021-02-23T08:13:16.000' AS DateTime), NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (10, 7, CAST(N'2021-02-23T08:07:40.000' AS DateTime), CAST(N'2021-02-23T08:12:39.000' AS DateTime), NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (11, 8, CAST(N'2021-02-23T08:08:17.000' AS DateTime), CAST(N'2021-02-23T08:13:54.000' AS DateTime), NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (12, 9, CAST(N'2021-02-23T08:10:10.000' AS DateTime), NULL, NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (13, 1, CAST(N'2021-02-23T08:47:35.000' AS DateTime), CAST(N'2021-02-23T08:47:42.000' AS DateTime), NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (14, 2, CAST(N'2021-02-23T08:47:53.000' AS DateTime), CAST(N'2021-02-23T08:48:00.000' AS DateTime), N'กินข้าว')
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (15, 3, CAST(N'2021-02-23T08:50:21.000' AS DateTime), CAST(N'2021-02-23T08:50:25.000' AS DateTime), N'เข้าห้องน้ำ')
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (16, 1, CAST(N'2021-02-23T20:05:09.000' AS DateTime), CAST(N'2021-02-23T20:05:12.000' AS DateTime), NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (17, 2, CAST(N'2021-02-23T20:05:28.000' AS DateTime), CAST(N'2021-02-23T20:05:30.000' AS DateTime), NULL)
INSERT [dbo].[History] ([HistoryID], [CarID], [EnterTimestamp], [ExitTimestamp], [Activity]) VALUES (18, 3, CAST(N'2021-02-23T20:07:59.000' AS DateTime), CAST(N'2021-02-23T20:08:01.000' AS DateTime), NULL)
SET IDENTITY_INSERT [dbo].[History] OFF
GO
SET IDENTITY_INSERT [dbo].[User] ON 

INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType], [Status]) VALUES (1, N'Opal', N'6010017', N'Nuntanuch', N'Tharapong', N'Admin', N'Active')
INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType], [Status]) VALUES (2, N'Pim', N'6013633', N'Kamonrut', N'Vorrawongprasert', N'Admin', N'Active')
INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType], [Status]) VALUES (3, N'Nueng', N'1234567', N'Chayapol', N'Moemeng', N'User', N'Active')
INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType], [Status]) VALUES (5, N'Nut', N'1234567', N'Naraboodee', N'Anantapornkit', N'User', N'Active')
INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType], [Status]) VALUES (6, N'sdfdsf', N'112233', N'aabbcc', N'aabbcc', N'Admin', N'Active')
INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType], [Status]) VALUES (7, N'nazz', N'13579', N'abc', N'naxx', N'User', N'Active')
INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType], [Status]) VALUES (8, N'oba', N'aacc', N'aaccss', N'acsasc', N'Admin', N'Active')
INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType], [Status]) VALUES (9, N'oppa', N'opaopaopaopa', N'opaopa', N'opaopaopa', N'User', N'Active')
INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType], [Status]) VALUES (10, N'xoxo', N'xoxoxoxo', N'xoxo', N'xoxo', N'User', N'Active')
INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType], [Status]) VALUES (11, N'accident', N'baba', N'acc', N'baba', N'Admin', N'Active')
INSERT [dbo].[User] ([UserID], [UserName], [Password], [FirstName], [LastName], [UserType], [Status]) VALUES (12, N'lala', N'ababa', N'abab', N'abab', N'User', N'Active')
SET IDENTITY_INSERT [dbo].[User] OFF
GO
SET IDENTITY_INSERT [dbo].[Incident] ON 

INSERT [dbo].[Incident] ([IncidentID], [CarID], [UserID], [Description], [Type], [StartTimestamp], [EndTimestamp], [Status]) VALUES (1, 1, 2, N'ลืมบัตรเครดิต', N'Note', CAST(N'2021-02-23T08:18:09.000' AS DateTime), NULL, N'Active')
INSERT [dbo].[Incident] ([IncidentID], [CarID], [UserID], [Description], [Type], [StartTimestamp], [EndTimestamp], [Status]) VALUES (2, 2, 2, N'ขโมยเงิน', N'Blacklist', CAST(N'2021-02-23T08:29:12.000' AS DateTime), NULL, N'Active')
INSERT [dbo].[Incident] ([IncidentID], [CarID], [UserID], [Description], [Type], [StartTimestamp], [EndTimestamp], [Status]) VALUES (3, 3, 1, N'คนตรวจปั้ม โหด', N'VIP', CAST(N'2021-02-23T08:30:41.000' AS DateTime), CAST(N'2021-02-23T08:31:04.000' AS DateTime), N'Inactive')
INSERT [dbo].[Incident] ([IncidentID], [CarID], [UserID], [Description], [Type], [StartTimestamp], [EndTimestamp], [Status]) VALUES (4, 3, 1, N'คนตรวจปั๊ม', N'VIP', CAST(N'2021-02-23T08:32:16.000' AS DateTime), NULL, N'Active')
INSERT [dbo].[Incident] ([IncidentID], [CarID], [UserID], [Description], [Type], [StartTimestamp], [EndTimestamp], [Status]) VALUES (5, 10, 1, N'ต้มตุ๋น', N'Blacklist', CAST(N'2021-02-23T08:34:26.000' AS DateTime), NULL, N'Active')
INSERT [dbo].[Incident] ([IncidentID], [CarID], [UserID], [Description], [Type], [StartTimestamp], [EndTimestamp], [Status]) VALUES (6, 11, 1, N'..', N'Note', CAST(N'2021-02-23T20:02:40.000' AS DateTime), CAST(N'2021-02-23T20:03:31.000' AS DateTime), N'Inactive')
SET IDENTITY_INSERT [dbo].[Incident] OFF
GO
